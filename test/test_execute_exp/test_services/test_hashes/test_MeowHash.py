import unittest, os, sys
from unittest.mock import Mock, call

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.hashes.MeowHash import MeowHash


class TestMeowHash(unittest.TestCase):
    def setUp(self):
        # Mocks para simular a serialização de args e kwargs
        self.first_output = os.urandom(16)
        self.second_output = os.urandom(16)
        self.third_output = os.urandom(16)
        self.serializer = Mock()
        
        self.serializer.dumps = Mock() 
        self.serializer.clean_data = Mock(side_effect=lambda x: x)
        
        self.hash = MeowHash(self.serializer)

    def test_hash_consistency(self):
        """
        Testa se o mesmo input produz o mesmo hash (Estabilidade).
        """
        source = 'def minha_funcao(): return 42'
        args = [1, 2, 3]
        kwargs = {'a': 'b'}

        # Configura o mock para as chamadas a dumps (args, kwargs)
        self.serializer.dumps.side_effect = [self.first_output, self.second_output]
        hash1 = self.hash.get_id(source, fun_args=args, fun_kwargs=kwargs)

        # Reconfigura o mock para a segunda chamada, usando os mesmos bytes
        self.serializer.dumps.side_effect = [self.first_output, self.second_output]
        hash2 = self.hash.get_id(source, fun_args=args, fun_kwargs=kwargs)

        self.assertEqual(hash1, hash2, "O mesmo input não gerou hashes idênticos (Falha na Estabilidade).")
        self.assertEqual(len(hash1), 32, "O hash não tem o tamanho correto (32 caracteres hex).")
        self.assertTrue(all(c in '0123456789abcdef' for c in hash1), "O hash contém caracteres não hexadecimais.")


    def test_hash_non_collision(self):
        """
        Testa se inputs diferentes geram hashes diferentes (Não-colisão).
        """
        source1 = 'def f(x): return x + 1'
        source2 = 'def f(x): return x + 2' 

        # --- Call 1: hash1 (Args: [5], usa self.first_output) ---
        self.serializer.dumps.side_effect = [self.first_output]
        hash1 = self.hash.get_id(source1, fun_args=[5])

        # --- Call 2: hash2 (Source changes, usa self.second_output) ---
        self.serializer.dumps.side_effect = [self.second_output]
        hash2 = self.hash.get_id(source2, fun_args=[5])

        # --- Call 3: hash3 (Args change to [6], usa self.third_output) ---
        self.serializer.dumps.side_effect = [self.third_output]
        hash3 = self.hash.get_id(source1, fun_args=[6])
        
        # Test 1: Source change (hash1 vs hash2). 
        self.assertNotEqual(hash1, hash2, "Códigos fonte diferentes geraram o mesmo hash (Colisão).")

        # Test 2: Arg change (hash1 vs hash3). 
        self.assertNotEqual(hash1, hash3, "Argumentos diferentes geraram o mesmo hash (Colisão).")

        # Test 3: Mixed change (hash2 vs hash3). 
        self.assertNotEqual(hash2, hash3, "Diferentes inputs geraram o mesmo hash (Colisão).")


if __name__ == '__main__':
    unittest.main()