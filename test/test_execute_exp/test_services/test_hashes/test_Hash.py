import unittest, os, sys
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.hashes.Hash import Hash


class TestHash(unittest.TestCase):
    def setUp(self):
        self.first_output = os.urandom(16)
        self.second_output = os.urandom(16)
        self.serializer = Mock()
        self.serializer.dumps = Mock(side_effect=[self.first_output, self.second_output])

        self.hash = Hash(self.serializer)

        self.hash._hash = Mock()

    def test_get_id_without_fun_args(self):
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'
        self.hash.get_id(source, fun_kwargs={'z': -12.5})

        expected_args = ((str(self.first_output) + source).encode('utf'),)

        self.hash._hash.assert_called_once()
        self.assertTupleEqual(self.hash._hash.call_args[0], expected_args)
        self.assertDictEqual(self.hash._hash.call_args[1], {})

    def test_get_id_without_fun_kwargs(self):
        source = 'print("Testando!")\nos.path.exists("/")\nrandom.randint()\nreturn x + y / -z'
        self.hash.get_id(source, fun_args=[-1.227, 0])

        expected_args = ((str(self.first_output) + source).encode('utf'),)

        self.hash._hash.assert_called_once()
        self.assertTupleEqual(self.hash._hash.call_args[0], expected_args)
        self.assertDictEqual(self.hash._hash.call_args[1], {})

    def test_get_id_only_with_fun_source(self):
        source = 'print("Testando!")\nreturn x / y ** 2'
        self.hash.get_id(source)

        expected_args = (("b''" + source).encode('utf'),)

        self.hash._hash.assert_called_once()
        self.assertTupleEqual(self.hash._hash.call_args[0], expected_args)
        self.assertDictEqual(self.hash._hash.call_args[1], {})

    def test_get_id_with_source_args_and_kwargs(self):
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'
        self.hash.get_id(source, fun_args=[-1.227, 0], fun_kwargs={'z': -12.5})

        expected_args = ((str(self.first_output + self.second_output) + source).encode('utf'),)

        self.hash._hash.assert_called_once()
        self.assertTupleEqual(self.hash._hash.call_args[0], expected_args)
        self.assertDictEqual(self.hash._hash.call_args[1], {})


if __name__ == '__main__':
    unittest.main()
