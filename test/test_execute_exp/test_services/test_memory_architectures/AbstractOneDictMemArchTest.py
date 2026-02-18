import unittest, os, sys, time
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.entitites.CacheData import CacheData

from test_execute_exp.test_services.test_memory_architectures.AbstractMemArchTest import AbstractMemArchTest


class AbstractOneDictMemArchTest(AbstractMemArchTest):
    def test_get_initial_cache_entries_using_a_thread_simulating_race_condition(self):
        records = {'func_call_hash1': CacheData('func_call_hash1', True),
                   'func_call_hash2': CacheData('func_call_hash2', 10.123),
                   'func_call_hash3': CacheData('func_call_hash3', {1, -3, 'test'})}
        self.retrieval_strategy.get_initial_cache_entries = Mock(return_value=records)
        self.mem_arch._use_threads = True
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.acquire()
        self.mem_arch.get_initial_cache_entries()

        time.sleep(0.2)
        self.retrieval_strategy.get_initial_cache_entries.assert_called_once()

        for i in range(5):  # Checking that thread is waiting for the semaphore to be released
            self.assertTrue(self.mem_arch._thread.is_alive())
            self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, {})
            time.sleep(0.2)
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.release()

        while self.mem_arch._thread.is_alive(): pass
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, records)

    def test_get_function_entries_from_storage_using_a_thread_simulating_race_condition(self):
        original_data = {'fc_hash0': CacheData('fc_hash0', True, func_name='f0'),
                         'fc_hash00': CacheData('fc_hash00', False, func_name='f0')}
        loaded_data = {'fc_hash1': CacheData('fc_hash1', (1, 2, 3), func_name='f1'),
                       'fc_hash2': CacheData('fc_hash2', {1, 2, 3}, func_name='f1')}
        self.mem_arch._DATA_DICTIONARY = original_data
        self.retrieval_strategy.get_function_cache_entries = Mock(return_value=loaded_data)
        self.retrieval_strategy.get_cache_entry = Mock(return_value=loaded_data['fc_hash1'])
        self.mem_arch._use_threads = True
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.acquire()

        c = self.mem_arch.get_cache_entry('fc_hash1', 'f1')

        time.sleep(0.2)

        self.assertTupleEqual(c, (1, 2, 3))
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.retrieval_strategy.get_cache_entry.assert_called_once()

        for i in range(5):  # Checking that thread is waiting for the semaphore to be released
            self.assertTrue(self.mem_arch._thread.is_alive())
            self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, original_data)
            time.sleep(0.2)
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.release()

        while self.mem_arch._thread.is_alive(): pass

        loaded_data.update(original_data)
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, loaded_data)


# XXX : IMPLEMENTAR TESTE QUE CHAME FUNÇÃO PASSANDO FUNC_NAME DIFERENTE DE NULL, MAS O RETRIEVAL STRATEGY É LAZY OU EAGER

if __name__ == '__main__':
    unittest.main()
