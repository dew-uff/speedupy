import unittest, os, sys, io
from unittest.mock import patch, Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.SpeeduPySettings import SpeeduPySettings
from execute_exp.services.storages.Storage import Storage
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy
from execute_exp.services.memory_architecures.AbstractOneDictMemArch import AbstractOneDictMemArch
from entities.CacheData import CacheData
import time, threading, copy

class TestIntPy(unittest.TestCase):
    def setUp(self):
        self.storage = Mock(Storage)
        self.retrieval_strategy = Mock(AbstractRetrievalStrategy)
        self.mem_arch = AbstractOneDictMemArch(self.storage, self.retrieval_strategy, False)

    def test_get_initial_cache_entries_when_retrieval_strategy_doesnt_load_records(self):
        self.retrieval_strategy.get_initial_cache_entries = Mock(return_value={})
        self.mem_arch.get_initial_cache_entries()
        
        self.retrieval_strategy.get_initial_cache_entries.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, {})

    def test_get_initial_cache_entries_when_some_records_are_loaded_from_storage(self):
        records = {'func_call_hash1':CacheData('func_call_hash1', True),
                   'func_call_hash2':CacheData('func_call_hash2', 10.123),
                   'func_call_hash3':CacheData('func_call_hash3', {1, -3, 'test'})}
        self.retrieval_strategy.get_initial_cache_entries = Mock(return_value=records)
        self.mem_arch.get_initial_cache_entries()

        self.retrieval_strategy.get_initial_cache_entries.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, records)

    def test_get_initial_cache_entries_using_a_thread(self):
        records = {'func_call_hash1':CacheData('func_call_hash1', True),
                   'func_call_hash2':CacheData('func_call_hash2', 10.123),
                   'func_call_hash3':CacheData('func_call_hash3', {1, -3, 'test'})}
        self.retrieval_strategy.get_initial_cache_entries = Mock(return_value=records)
        self.mem_arch._use_threads = True
        self.mem_arch.get_initial_cache_entries()
        
        while self.mem_arch._thread.is_alive(): pass
        self.retrieval_strategy.get_initial_cache_entries.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, records)

    def test_get_initial_cache_entries_using_a_thread_simulating_race_condition(self):
        records = {'func_call_hash1':CacheData('func_call_hash1', True),
                   'func_call_hash2':CacheData('func_call_hash2', 10.123),
                   'func_call_hash3':CacheData('func_call_hash3', {1, -3, 'test'})}
        self.retrieval_strategy.get_initial_cache_entries = Mock(return_value=records)
        self.mem_arch._use_threads = True
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.acquire()
        self.mem_arch.get_initial_cache_entries()
        
        time.sleep(0.2)
        self.retrieval_strategy.get_initial_cache_entries.assert_called_once()

        for i in range(5): #Checking that thread is waiting for the semaphore to be released
            self.assertTrue(self.mem_arch._thread.is_alive())
            self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, {})
            time.sleep(0.2)
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.release()

        while self.mem_arch._thread.is_alive(): pass
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, records)

    def test_get_cache_entry_from_dict_when_dict_is_empty(self):
        c = self.mem_arch._get_cache_entry_from_dict('func_call_hash')
        self.assertIsNone(c)

    def test_get_cache_entry_from_dict_when_dict_has_the_requested_data(self):
        self.mem_arch._DATA_DICTIONARY = {'fc_hash1': CacheData('fc_hash1', 10),
                                          'fc_hash2': CacheData('fc_hash2', 'test'),
                                          'fc_hash3': CacheData('fc_hash3', False)}
        c = self.mem_arch._get_cache_entry_from_dict('fc_hash2')
        self.assertEqual(c, self.mem_arch._DATA_DICTIONARY['fc_hash2'])

    def test_get_cache_entry_from_dict_when_dict_doesnt_have_the_requested_data(self):
        self.mem_arch._DATA_DICTIONARY = {'fc_hash1': CacheData('fc_hash1', 10),
                                          'fc_hash2': CacheData('fc_hash2', 'test'),
                                          'fc_hash3': CacheData('fc_hash3', False)}
        c = self.mem_arch._get_cache_entry_from_dict('fc_hash5')
        self.assertIsNone(c)

    
    def test_get_cache_entry_from_dict_while_dict_is_being_filled_with_data(self):
        def fill_dict():
            start = time.perf_counter()
            end = time.perf_counter()
            i = 0
            while (end - start) < 1:
                self.mem_arch._DATA_DICTIONARY[f'fc_hash{i}'] = CacheData(f'fc_hash{i}', i)
                end = time.perf_counter()
                i += 1

        t = threading.Thread(target=fill_dict)
        t.start()
        aux = 0
        while t.is_alive():
            c = self.mem_arch._get_cache_entry_from_dict('function_call_hash')
            self.assertIsNone(c)
            aux += 1
        self.assertTrue(aux > 0)

    def test_get_cache_entry_from_dict_while_dict_is_being_filled_with_the_requested_data(self):
        def fill_dict():
            time.sleep(0.2)
            start = time.perf_counter()
            end = time.perf_counter()
            i = 0
            while (end - start) < 1:
                self.mem_arch._DATA_DICTIONARY[f'fc_hash{i}'] = CacheData(f'fc_hash{i}', i)
                end = time.perf_counter()
                i += 1
        
        t = threading.Thread(target=fill_dict)
        t.start()
        aux1, aux2 = 0, 0
        while t.is_alive():
            c = self.mem_arch._get_cache_entry_from_dict('fc_hash100')
            try:
                self.assertIsNone(c)
                aux1 += 1
            except AssertionError:
                self.assertEqual(c, self.mem_arch._DATA_DICTIONARY['fc_hash100'])
                aux2 += 1
        self.assertTrue(aux1 > 0)
        self.assertTrue(aux2 > 0)

    def test_get_cache_entry_from_storage_when_loading_a_function_call_record_that_doesnt_exist_on_storage(self):
        self.retrieval_strategy.get_cache_entry = Mock(return_value=None)
        self.mem_arch._get_function_entries_from_storage = Mock()
        
        c = self.mem_arch._get_cache_entry_from_storage('func_call_hash')

        self.assertIsNone(c)
        self.mem_arch._get_function_entries_from_storage.assert_not_called()
        self.retrieval_strategy.get_cache_entry.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, {})

    def test_get_cache_entry_from_storage_when_loading_a_function_call_record_that_exists_on_storage(self):
        cache_data = CacheData('func_call_hash', True)
        self.retrieval_strategy.get_cache_entry = Mock(return_value=cache_data)
        self.mem_arch._get_function_entries_from_storage = Mock()
        
        c = self.mem_arch._get_cache_entry_from_storage('func_call_hash')

        self.assertEqual(c, cache_data)
        self.mem_arch._get_function_entries_from_storage.assert_not_called()
        self.retrieval_strategy.get_cache_entry.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, {'func_call_hash': cache_data})

    def test_get_function_entries_from_storage_when_dict_is_empty_and_some_records_are_loaded(self):
        loaded_data = {'fc_hash1':CacheData('fc_hash1', (1, 2, 3), func_name='f1'),
                       'fc_hash2':CacheData('fc_hash2', {1, 2, 3}, func_name='f1')}
        self.retrieval_strategy.get_function_cache_entries = Mock(return_value=loaded_data)
        self.retrieval_strategy.get_cache_entry = Mock()
        
        c = self.mem_arch._get_function_entries_from_storage('fc_hash1', 'f1')

        self.assertEqual(c, loaded_data['fc_hash1'])
        self.retrieval_strategy.get_cache_entry.assert_not_called()
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, loaded_data)

    def test_get_function_entries_from_storage_when_dict_already_have_some_records_and_new_records_are_loaded(self):
        original_data = {'fc_hash0':CacheData('fc_hash0', True, func_name='f0'),
                         'fc_hash00':CacheData('fc_hash00', False, func_name='f0')}
        loaded_data = {'fc_hash1':CacheData('fc_hash1', (1, 2, 3), func_name='f1'),
                       'fc_hash2':CacheData('fc_hash2', {1, 2, 3}, func_name='f1')}
        self.mem_arch._DATA_DICTIONARY = {k:v for k, v in original_data.items()}
        self.retrieval_strategy.get_function_cache_entries = Mock(return_value=loaded_data)
        self.retrieval_strategy.get_cache_entry = Mock()
        
        c = self.mem_arch._get_function_entries_from_storage('fc_hash1', 'f1')

        loaded_data.update(original_data)
        self.assertEqual(c, loaded_data['fc_hash1'])
        self.retrieval_strategy.get_cache_entry.assert_not_called()
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, loaded_data)

    def test_get_function_entries_from_storage_when_no_records_are_loaded(self):
        original_data = {'fc_hash0':CacheData('fc_hash0', True, func_name='f0'),
                         'fc_hash00':CacheData('fc_hash00', False, func_name='f0')}
        self.mem_arch._DATA_DICTIONARY = {k:v for k, v in original_data.items()}
        self.retrieval_strategy.get_function_cache_entries = Mock(return_value={})
        self.retrieval_strategy.get_cache_entry = Mock()
        
        c = self.mem_arch._get_function_entries_from_storage('fc_hash1', 'f1')

        self.assertIsNone(c)
        self.retrieval_strategy.get_cache_entry.assert_not_called()
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, original_data)

    def test_get_function_entries_from_storage_when_some_records_are_loaded_but_the_requested_function_call_record_doesnt_exist(self):
        original_data = {'fc_hash0':CacheData('fc_hash0', True, func_name='f0'),
                         'fc_hash00':CacheData('fc_hash00', False, func_name='f0')}
        loaded_data = {'fc_hash1':CacheData('fc_hash1', (1, 2, 3), func_name='f1'),
                       'fc_hash2':CacheData('fc_hash2', {1, 2, 3}, func_name='f1')}
        self.mem_arch._DATA_DICTIONARY = {k:v for k, v in original_data.items()}
        self.retrieval_strategy.get_function_cache_entries = Mock(return_value=loaded_data)
        self.retrieval_strategy.get_cache_entry = Mock()
        
        c = self.mem_arch._get_function_entries_from_storage('fc_hash5', 'f1')

        loaded_data.update(original_data)
        self.assertIsNone(c)
        self.retrieval_strategy.get_cache_entry.assert_not_called()
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, loaded_data)

    def test_get_function_entries_from_storage_using_a_thread_when_the_requested_function_call_exists(self):
        original_data = {'fc_hash0':CacheData('fc_hash0', True, func_name='f0'),
                         'fc_hash00':CacheData('fc_hash00', False, func_name='f0')}
        loaded_data = {'fc_hash1':CacheData('fc_hash1', (1, 2, 3), func_name='f1'),
                       'fc_hash2':CacheData('fc_hash2', {1, 2, 3}, func_name='f1')}
        self.mem_arch._DATA_DICTIONARY = {k:v for k, v in original_data.items()}
        self.retrieval_strategy.get_function_cache_entries = Mock(return_value=loaded_data)
        self.retrieval_strategy.get_cache_entry = Mock(return_value=loaded_data['fc_hash1'])
        self.mem_arch._use_threads = True

        c = self.mem_arch._get_function_entries_from_storage('fc_hash1', 'f1')
        while self.mem_arch._thread.is_alive(): pass

        loaded_data.update(original_data)
        self.assertEqual(c, loaded_data['fc_hash1'])
        self.retrieval_strategy.get_cache_entry.assert_called_once()
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, loaded_data)

    def test_get_function_entries_from_storage_using_a_thread_when_the_requested_function_call_doesnt_exist(self):
        original_data = {'fc_hash0':CacheData('fc_hash0', True, func_name='f0'),
                         'fc_hash00':CacheData('fc_hash00', False, func_name='f0')}
        loaded_data = {'fc_hash1':CacheData('fc_hash1', (1, 2, 3), func_name='f1'),
                       'fc_hash2':CacheData('fc_hash2', {1, 2, 3}, func_name='f1')}
        self.mem_arch._DATA_DICTIONARY = {k:v for k, v in original_data.items()}
        self.retrieval_strategy.get_function_cache_entries = Mock(return_value=loaded_data)
        self.retrieval_strategy.get_cache_entry = Mock(return_value=None)
        self.mem_arch._use_threads = True

        c = self.mem_arch._get_function_entries_from_storage('fc_hash60', 'f1')
        while self.mem_arch._thread.is_alive(): pass

        loaded_data.update(original_data)
        self.assertIsNone(c)
        self.retrieval_strategy.get_cache_entry.assert_called_once()
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, loaded_data)

    def test_get_function_entries_from_storage_using_a_thread_simulating_race_condition(self):
        original_data = {'fc_hash0':CacheData('fc_hash0', True, func_name='f0'),
                         'fc_hash00':CacheData('fc_hash00', False, func_name='f0')}
        loaded_data = {'fc_hash1':CacheData('fc_hash1', (1, 2, 3), func_name='f1'),
                       'fc_hash2':CacheData('fc_hash2', {1, 2, 3}, func_name='f1')}
        self.mem_arch._DATA_DICTIONARY = {k:v for k, v in original_data.items()}
        self.retrieval_strategy.get_function_cache_entries = Mock(return_value=loaded_data)
        self.retrieval_strategy.get_cache_entry = Mock(return_value=loaded_data['fc_hash1'])
        self.mem_arch._use_threads = True
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.acquire()

        c = self.mem_arch._get_function_entries_from_storage('fc_hash1', 'f1')

        time.sleep(0.2)
        self.assertEqual(c, loaded_data['fc_hash1'])
        self.retrieval_strategy.get_cache_entry.assert_called_once()
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()

        for i in range(5): #Checking that thread is waiting for the semaphore to be released
            self.assertTrue(self.mem_arch._thread.is_alive())
            self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, original_data)
            time.sleep(0.2)
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.release()

        while self.mem_arch._thread.is_alive(): pass

        loaded_data.update(original_data)
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, loaded_data)
