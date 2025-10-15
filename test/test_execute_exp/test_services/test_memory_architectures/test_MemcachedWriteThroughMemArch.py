import unittest, os, sys, random
from unittest.mock import patch, Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

# Importa as classes necessárias para o teste
from execute_exp.services.memory_architecures.MemcachedWriteThroughMemArch import MemcachedWriteThroughMemArch
from execute_exp.entitites.CacheData import CacheData

class TestMemcachedWriteThrough(unittest.TestCase):

    # O decorator @patch substitui a classe 'BancoMemcached' por um "dublê" (Mock)
    # durante a execução do teste. Isso nos permite controlar e verificar seu comportamento.
    @patch('execute_exp.services.memory_architecures.MemcachedWriteThroughMemArch.BancoMemcached')
    def setUp(self, mock_banco_memcached):
        """Este método é executado antes de cada teste da classe."""
        
        # 1. Cria um mock para a RetrievalStrategy, que simula o acesso ao banco de dados persistente.
        self.mock_retrieval_strategy = Mock()
        
        # 2. Cria a instância da classe que queremos testar (o "Sistema Sob Teste").
        # Ela receberá o mock da retrieval strategy.
        self.mem_arch = MemcachedWriteThroughMemArch(
            retrieval_strategy=self.mock_retrieval_strategy,
            use_threads=False
        )
        
        # 3. Pega uma referência ao mock do BancoMemcached que foi injetado pelo @patch.
        # Isso nos permite controlar o cliente memcached.
        self.mock_memcached_client = self.mem_arch.memcached

    def test_get_cache_entry_when_hit(self):
        """Cenário 1: O dado é encontrado no Memcached (cache hit)."""
        
        # PREPARAÇÃO: Programamos o mock do memcached para retornar um valor simulado.
        self.mock_memcached_client.get.return_value = CacheData("hash123", "resultado_do_cache")
        
        # AÇÃO: Executamos o método que queremos testar.
        result = self.mem_arch.get_cache_entry("hash123")

        # VERIFICAÇÃO:
        # O resultado retornado é o esperado?
        self.assertEqual(result, "resultado_do_cache")
        # O método 'get' do memcached foi chamado?
        self.mock_memcached_client.get.assert_called_once_with("hash123")
        # O storage persistente NÃO foi acessado? (essencial para um cache hit)
        self.mock_retrieval_strategy.get_cache_entry.assert_not_called()

    def test_get_cache_entry_when_miss(self):
        """Cenário 2: O dado não é encontrado no Memcached (cache miss) e precisa ser buscado no storage."""
        
        # PREPARAÇÃO:
        # Programamos o memcached para não encontrar nada (retornar None).
        self.mock_memcached_client.get.return_value = None
        # Programamos o storage persistente para encontrar o dado.
        persistent_data = CacheData("hash123", "resultado_do_storage")
        self.mock_retrieval_strategy.get_cache_entry.return_value = persistent_data
        
        # AÇÃO: Executamos o método.
        result = self.mem_arch.get_cache_entry("hash123")

        # VERIFICAÇÃO:
        # O resultado retornado é o do storage persistente?
        self.assertEqual(result, "resultado_do_storage")
        # O memcached foi consultado primeiro?
        self.mock_memcached_client.get.assert_called_once_with("hash123")
        # O storage persistente foi consultado em seguida?
        self.mock_retrieval_strategy.get_cache_entry.assert_called_once_with("hash123", None)
        # O memcached foi atualizado com o novo dado para a próxima busca (lógica de read-through)?
        self.mock_memcached_client.set.assert_called_once_with("hash123", persistent_data)

    def test_create_cache_entry_writes_through(self):
        """Verifica se a política 'write-through' escreve no cache E no storage ao mesmo tempo."""
        
        # AÇÃO:
        self.mem_arch.create_cache_entry("hash123", "resultado")

        # VERIFICAÇÃO:
        # Foi chamado o 'set' no memcached?
        self.mock_memcached_client.set.assert_called_once()
        # Foi chamado o 'save_cache_data' no storage persistente?
        self.mock_retrieval_strategy.save_cache_data.assert_called_once()
        
    def test_save_new_cache_entries_does_nothing(self):
        """No modo write-through, este método não deve fazer nada, pois os dados já foram salvos."""
        
        # AÇÃO:
        self.mem_arch.save_new_cache_entries()
        
        # VERIFICAÇÃO: O método para salvar no storage NÃO foi chamado aqui.
        self.mock_retrieval_strategy.save_cache_data.assert_not_called()