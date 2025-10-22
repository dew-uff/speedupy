import unittest, os, sys, random
from unittest.mock import patch, Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.memory_architecures.MemcachedWriteThroughMemArch import MemcachedWriteThroughMemArch
from execute_exp.entitites.CacheData import CacheData

class TestMemcachedWriteThrough(unittest.TestCase):

    @patch('execute_exp.services.memory_architecures.MemcachedWriteThroughMemArch.BancoMemcached')
    def setUp(self, mock_banco_memcached):
        
        self.mock_retrieval_strategy = Mock()
        self.mem_arch = MemcachedWriteThroughMemArch(
            retrieval_strategy=self.mock_retrieval_strategy,
            use_threads=False
        )
        self.mock_memcached_client = self.mem_arch.memcached

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

    def test_create_cache_entry_writes_through(self):

        self.mem_arch.create_cache_entry("hash123", "resultado")
        self.mock_memcached_client.set.assert_called_once()
        self.mock_retrieval_strategy.save_cache_data.assert_called_once()
        
    def test_save_new_cache_entries_does_nothing(self):

        self.mem_arch.save_new_cache_entries()
        self.mock_retrieval_strategy.save_cache_data.assert_not_called()