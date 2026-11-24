import unittest, os, sys, random, threading
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.retrieval_strategies.EagerRetrieval import EagerRetrieval
from execute_exp.services.memory_architecures.OneDictAllDataOneDictNewDataMemArch import OneDictAllDataOneDictNewDataMemArch
from execute_exp.services.storages.Storage import Storage


class TestEagerRetrieval(unittest.TestCase):
    def setUp(self):
        self.storage = Mock(Storage)
        self.eager_retrieval = EagerRetrieval(self.storage)

    def test_get_initial_cache_entries_when_storage_is_empty(self):
        use_thread = random.choice([True, False])
        self.storage.get_all_cached_data = Mock(return_value={})

        data = self.eager_retrieval.get_initial_cache_entries(use_thread=use_thread)

        self.assertDictEqual(data, {})
        self.storage.get_all_cached_data.assert_called_once_with(use_isolated_connection=use_thread)

    def test_get_initial_cache_entries_when_storage_is_not_empty(self):
        use_thread = random.choice([True, False])
        expected_data = {'fc_hash1': CacheData('fc_hash1', True),
                         'fc_hash2': CacheData('fc_hash2', (1,)),
                         'fc_hash3': CacheData('fc_hash3', [False])}
        self.storage.get_all_cached_data = Mock(return_value=expected_data)

        data = self.eager_retrieval.get_initial_cache_entries(use_thread=use_thread)

        self.assertDictEqual(data, expected_data)
        self.storage.get_all_cached_data.assert_called_once_with(use_isolated_connection=use_thread)

    def test_get_cache_entry_before_initial_loading_when_entry_exists(self):
        data = CacheData('fc_hash1', (1, 2, 3))
        self.storage.get_cached_data_of_a_function_call = Mock(return_value=data)

        c = self.eager_retrieval.get_cache_entry('fc_hash1', 'f1')

        self.storage.get_cached_data_of_a_function_call.assert_called_once_with('fc_hash1', func_name=None)
        self.assertEqual(c, data)

    def test_get_cache_entry_before_initial_loading_when_entry_does_not_exist(self):
        self.storage.get_cached_data_of_a_function_call = Mock(return_value=None)

        c = self.eager_retrieval.get_cache_entry('fc_hash1', 'f1')

        self.storage.get_cached_data_of_a_function_call.assert_called_once_with('fc_hash1', func_name=None)
        self.assertIsNone(c)

    def test_get_cache_entry_after_initial_loading_when_entry_was_loaded(self):
        data = CacheData('fc_hash1', (1, 2, 3))
        self.storage.get_all_cached_data = Mock(return_value={'fc_hash1': data})
        self.storage.get_cached_data_of_a_function_call = Mock(return_value=None)
        self.eager_retrieval.get_initial_cache_entries(use_thread=random.choice([True, False]))

        c = self.eager_retrieval.get_cache_entry('fc_hash1', 'f1')

        self.assertEqual(c, data)
        self.storage.get_cached_data_of_a_function_call.assert_not_called()

    def test_get_cache_entry_after_initial_loading_when_entry_was_not_loaded(self):
        self.storage.get_all_cached_data = Mock(return_value={})
        self.storage.get_cached_data_of_a_function_call = Mock(return_value=None)
        self.eager_retrieval.get_initial_cache_entries(use_thread=random.choice([True, False]))

        c = self.eager_retrieval.get_cache_entry('fc_hash1', 'f1')

        self.assertIsNone(c)
        self.storage.get_cached_data_of_a_function_call.assert_not_called()

    def test_memory_architecture_does_not_recompute_a_call_while_the_loading_thread_runs(self):
        # Eager-thread end to end with a memory architecture: the loading thread
        # is held until the script has asked for a persisted result.
        data = CacheData('fc_hash1', (1, 2, 3))
        loading_released = threading.Event()
        def get_all_cached_data(use_isolated_connection=False):
            loading_released.wait(timeout=5)
            return {'fc_hash1': data}
        self.storage.get_all_cached_data = Mock(side_effect=get_all_cached_data)
        self.storage.get_cached_data_of_a_function_call = Mock(return_value=data)
        mem_arch = OneDictAllDataOneDictNewDataMemArch(self.eager_retrieval, True)
        mem_arch.get_initial_cache_entries()
        loading_thread = mem_arch._thread
        try:
            self.assertTrue(loading_thread.is_alive())

            c = mem_arch.get_cache_entry('fc_hash1', 'f1')

            self.assertTupleEqual(c, (1, 2, 3))
            self.storage.get_cached_data_of_a_function_call.assert_called_once_with('fc_hash1', func_name=None)
        finally:
            loading_released.set()
            loading_thread.join(timeout=5)
        self.assertFalse(loading_thread.is_alive())

        # After the loading, a call that is not in the cache does not access the storage.
        self.assertIsNone(mem_arch.get_cache_entry('fc_hash2', 'f1'))
        self.storage.get_cached_data_of_a_function_call.assert_called_once()

    def test_get_function_cache_entries(self):
        use_thread = random.choice([True, False])
        data = self.eager_retrieval.get_function_cache_entries('f1', use_thread=use_thread)
        self.assertDictEqual(data, {})

    def test_save_cache_data(self):
        self.storage.save_cache_data = Mock(return_value=None)
        conn = random.choice([True, False])
        data = {'fc_hash1': CacheData('fc_hash1', (1, 2, 3), func_name='f1'),
                'fc_hash2': CacheData('fc_hash2', True),
                'fc_hash3': CacheData('fc_hash3', -55.2, func_name='f3')}
        expected_data = {'fc_hash1': CacheData('fc_hash1', (1, 2, 3)),
                         'fc_hash2': CacheData('fc_hash2', True),
                         'fc_hash3': CacheData('fc_hash3', -55.2)}

        self.eager_retrieval.save_cache_data(data, use_isolated_connection=conn)

        self.storage.save_cache_data.assert_called_once_with(expected_data, use_isolated_connection=conn)


if __name__ == '__main__':
    unittest.main()
