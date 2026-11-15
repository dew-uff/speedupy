import unittest, os, sys, random
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split("test/")[0]
sys.path.append(project_folder)

from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.retrieval_strategies.EagerRetrieval import EagerRetrieval
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
        self.storage.get_all_cached_data.assert_called_once_with(
            use_isolated_connection=use_thread
        )

    def test_get_initial_cache_entries_when_storage_is_not_empty(self):
        use_thread = random.choice([True, False])
        expected_data = {
            "fc_hash1": CacheData("fc_hash1", True),
            "fc_hash2": CacheData("fc_hash2", (1,)),
            "fc_hash3": CacheData("fc_hash3", [False]),
        }
        self.storage.get_all_cached_data = Mock(return_value=expected_data)

        data = self.eager_retrieval.get_initial_cache_entries(use_thread=use_thread)

        self.assertDictEqual(data, expected_data)
        self.storage.get_all_cached_data.assert_called_once_with(
            use_isolated_connection=use_thread
        )

    def test_get_cache_entry(self):
        data = self.eager_retrieval.get_cache_entry("fc_hash1", "f1")
        self.assertIsNone(data)

    def test_get_function_cache_entries(self):
        use_thread = random.choice([True, False])
        data = self.eager_retrieval.get_function_cache_entries(
            "f1", use_thread=use_thread
        )
        self.assertDictEqual(data, {})

    def test_save_cache_data(self):
        self.storage.save_cache_data = Mock(return_value=None)
        conn = random.choice([True, False])
        data = {
            "fc_hash1": CacheData("fc_hash1", (1, 2, 3), func_name="f1"),
            "fc_hash2": CacheData("fc_hash2", True),
            "fc_hash3": CacheData("fc_hash3", -55.2, func_name="f3"),
        }
        expected_data = {
            "fc_hash1": CacheData("fc_hash1", (1, 2, 3)),
            "fc_hash2": CacheData("fc_hash2", True),
            "fc_hash3": CacheData("fc_hash3", -55.2),
        }

        self.eager_retrieval.save_cache_data(data, use_isolated_connection=conn)

        self.storage.save_cache_data.assert_called_once_with(
            expected_data, use_isolated_connection=conn
        )


if __name__ == "__main__":
    unittest.main()
