import unittest, os, sys, time

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.memory_architecures.AbstractMemcachedArch import AbstractMemcachedArch
from execute_exp.entitites.CacheData import CacheData

from typing import Dict
from pymemcache.client.base import PooledClient
from pymemcache.serde import pickle_serde
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch

from test_execute_exp.test_services.test_memory_architectures.AbstractMemArchTest import AbstractMemArchTest


#XXX: CONTINUAR TESTES!!!!
class TestAbstractMemcachedArch(AbstractMemArchTest, unittest.TestCase):
    def tearDown(self):
        super().tearDown()
        self.memcached.close()

    def create_instance(self) -> AbstractMemArch:
        self.cache_keys = []
        self.memcached = PooledClient(('127.0.0.1', 11211),
                             serializer=pickle_serde.serialize,
                             deserializer=pickle_serde.deserialize,
                             max_pool_size=2)
        self.memcached.flush_all()
        return AbstractMemcachedArch(self.retrieval_strategy, False)

    def assert_cache_on_RAM_equal(self, non_persisted_data:Dict[str, CacheData], persisted_data:Dict[str, CacheData]) -> None:
        time.sleep(0.1)  # Memcached need some time to insert elements to the database
        cache_data = non_persisted_data | persisted_data
        for k, v in cache_data.items():
            self.assertEqual(self.memcached.get(k), v)
        # self.assertListEqual(self.cache_keys, list(cache_data.keys()))

    def insert_data_on_cache_RAM(self, non_persisted_data:Dict[str, CacheData], persisted_data:Dict[str, CacheData]) -> None:
        self.memcached.set_many(non_persisted_data)
        self.memcached.set_many(persisted_data)
        # self.cache_keys += list(non_persisted_data.keys()) + list(persisted_data.keys())

    # XXX: VER SE SERÁ IMPLEMENTADO
    # def test_get_initial_cache_entries_using_a_thread_simulating_race_condition(self):
    #     records = {'func_call_hash1': CacheData('func_call_hash1', True),
    #                'func_call_hash2': CacheData('func_call_hash2', 10.123),
    #                'func_call_hash3': CacheData('func_call_hash3', {1, -3, 'test'})}
    #     self.retrieval_strategy.get_initial_cache_entries = Mock(return_value=records)
    #     self.mem_arch._use_threads = True
    #     self.mem_arch._DATA_DICTIONARY_SEMAPHORE.acquire()
    #     self.mem_arch.get_initial_cache_entries()

    #     time.sleep(0.2)
    #     self.retrieval_strategy.get_initial_cache_entries.assert_called_once()

    #     for i in range(5):  # Checking that thread is waiting for the semaphore to be released
    #         self.assertTrue(self.mem_arch._thread.is_alive())
    #         self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, {})
    #         time.sleep(0.2)
    #     self.mem_arch._DATA_DICTIONARY_SEMAPHORE.release()

    #     while self.mem_arch._thread.is_alive(): pass
    #     self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, records)

    # XXX: VER SE SERÁ IMPLEMENTADO
    # def test_get_cache_entry_when_miss(self):
    #     self.memcached.get.return_value = None
    #     persistent_data = CacheData("hash123", "resultado_do_storage")
    #     self.retrieval_strategy.get_cache_entry.return_value = persistent_data
    #     result = self.mem_arch.get_cache_entry("hash123")
    #     self.assertEqual(result, "resultado_do_storage")
    #     self.memcached.get.assert_called_once_with("hash123")
    #     self.retrieval_strategy.get_cache_entry.assert_called_once_with("hash123", None)
    #     self.memcached.set.assert_called_once_with("hash123", persistent_data)

    # def test_create_cache_entry_writes_only_to_memcached(self):

    #     self.mem_arch.create_cache_entry("hash123", "resultado")

    #     self.memcached.set.assert_called_once()
    #     self.retrieval_strategy.save_cache_data.assert_not_called()
    #     self.assertIn("hash123", self.mem_arch._dirty_entries)

    # XXX: VER SE SERÁ IMPLEMENTADO
    # def test_save_new_cache_entries_persists_dirty_data(self):
        
    #     self.mem_arch.create_cache_entry("hash123", "resultado")
        

    #     self.mem_arch.save_new_cache_entries()
        

    #     self.retrieval_strategy.save_cache_data.assert_called_once_with(
    #         self.mem_arch._dirty_entries
    #     )