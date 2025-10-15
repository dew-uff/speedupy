import unittest, os, sys, random
from unittest.mock import patch, Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.memory_architecures.MemcachedWriteBackMemArch import MemcachedWriteBackMemArch
from execute_exp.entitites.CacheData import CacheData

class TestMemcachedWriteBack(unittest.TestCase):

    # A preparação (@patch e setUp) é idêntica ao teste de Write-Through
    @patch('execute_exp.services.memory_architecures.MemcachedWriteBackMemArch.BancoMemcached')
    def setUp(self, mock_banco_memcached):
        self.mock_retrieval_strategy = Mock()
        self.mem_arch = MemcachedWriteBackMemArch(
            retrieval_strategy=self.mock_retrieval_strategy,
            use_threads=False
        )
        self.mock_memcached_client = self.mem_arch.memcached
    
    # Os testes de leitura (get) são idênticos, pois a lógica de leitura não muda entre as políticas.
    def test_get_cache_entry_when_hit(self):
        self.mock_memcached_client.get.return_value = CacheData("hash123", "resultado_do_cache")
        result = self.mem_arch.get_cache_entry("hash123")
        self.assertEqual(result, "resultado_do_cache")
        self.mock_memcached_client.get.assert_called_once_with("hash123")
        self.mock_retrieval_strategy.get_cache_entry.assert_not_called()

    def test_get_cache_entry_when_miss(self):
        self.mock_memcached_client.get.return_value = None
        persistent_data = CacheData("hash123", "resultado_do_storage")
        self.mock_retrieval_strategy.get_cache_entry.return_value = persistent_data
        result = self.mem_arch.get_cache_entry("hash123")
        self.assertEqual(result, "resultado_do_storage")
        self.mock_memcached_client.get.assert_called_once_with("hash123")
        self.mock_retrieval_strategy.get_cache_entry.assert_called_once_with("hash123", None)
        self.mock_memcached_client.set.assert_called_once_with("hash123", persistent_data)

    def test_create_cache_entry_writes_only_to_memcached(self):
        """Verifica se a política 'write-back' escreve APENAS no cache e marca o dado como 'sujo'."""
        
        # AÇÃO:
        self.mem_arch.create_cache_entry("hash123", "resultado")

        # VERIFICAÇÃO:
        # O 'set' do memcached foi chamado?
        self.mock_memcached_client.set.assert_called_once()
        # O storage persistente NÃO foi chamado ainda? (essencial para o write-back)
        self.mock_retrieval_strategy.save_cache_data.assert_not_called()
        # O dado foi adicionado ao dicionário de controle de dados "sujos"?
        self.assertIn("hash123", self.mem_arch._dirty_entries)

    def test_save_new_cache_entries_persists_dirty_data(self):
        """Verifica se 'save_new_cache_entries' salva os dados 'sujos' no storage."""
        
        # PREPARAÇÃO: Primeiro, criamos uma entrada "suja"
        self.mem_arch.create_cache_entry("hash123", "resultado")
        
        # AÇÃO: Agora, executamos o método que deve persistir os dados.
        self.mem_arch.save_new_cache_entries()
        
        # VERIFICAÇÃO: O storage persistente foi chamado com os dados corretos que estavam no buffer?
        self.mock_retrieval_strategy.save_cache_data.assert_called_once_with(
            self.mem_arch._dirty_entries
        )