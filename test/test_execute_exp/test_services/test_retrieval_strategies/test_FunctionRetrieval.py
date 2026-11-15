import copy
import os
import random
import sys
import unittest
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split("test/")[0]
sys.path.append(project_folder)

from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.retrieval_strategies.FunctionRetrieval import (
    FunctionRetrieval,
)
from execute_exp.services.storages.Storage import Storage


class TestFunctionRetrieval(unittest.TestCase):
    def setUp(self):
        self.storage = Mock(Storage)
        self.function_retrieval = FunctionRetrieval(self.storage)

    def test_get_initial_cache_entries(self):
        use_thread = random.choice([True, False])
        data = self.function_retrieval.get_initial_cache_entries(use_thread=use_thread)
        self.assertDictEqual(data, {})

    def test_get_cache_entry_when_entry_does_not_exist(self):
        self.storage.get_cached_data_of_a_function_call = Mock(return_value=None)

        c = self.function_retrieval.get_cache_entry("fc_hash1", "f1")

        self.storage.get_cached_data_of_a_function_call.assert_called_once_with(
            "fc_hash1", func_name="f1"
        )
        self.assertIsNone(c)

    def test_get_cache_entry_when_entry_exists(self):
        data = CacheData("fc_hash1", "teste")
        self.storage.get_cached_data_of_a_function_call = Mock(return_value=data)

        c = self.function_retrieval.get_cache_entry("fc_hash1", "f1")

        self.storage.get_cached_data_of_a_function_call.assert_called_once_with(
            "fc_hash1", func_name="f1"
        )
        self.assertEqual(c, data)

    def test_get_function_cache_entries_when_function_entries_already_loaded(self):
        use_thread = random.choice([True, False])
        self.storage.get_cached_data_of_a_function = Mock(
            return_value={
                "fc_hash1": CacheData("fc_hash1", False, func_name="f1"),
                "fc_hash2": CacheData("fc_hash2", 10, func_name="f1"),
            }
        )
        self.function_retrieval._functions_already_loaded_from_storage = ["f1"]

        data = self.function_retrieval.get_function_cache_entries(
            "f1", use_thread=use_thread
        )

        self.assertDictEqual(data, {})
        self.assertListEqual(
            self.function_retrieval._functions_already_loaded_from_storage, ["f1"]
        )
        self.storage.get_cached_data_of_a_function.assert_not_called()

    def test_get_function_cache_entries_when_no_entries_exist(self):
        use_thread = random.choice([True, False])
        self.storage.get_cached_data_of_a_function = Mock(return_value={})

        data = self.function_retrieval.get_function_cache_entries(
            "f1", use_thread=use_thread
        )

        self.assertDictEqual(data, {})
        self.assertListEqual(
            self.function_retrieval._functions_already_loaded_from_storage, ["f1"]
        )
        self.storage.get_cached_data_of_a_function.assert_called_once_with(
            "f1", use_isolated_connection=use_thread
        )

    def test_get_function_cache_entries_when_entries_exist(self):
        use_thread = random.choice([True, False])
        expected_data = {
            "fc_hash1": CacheData("fc_hash1", True, func_name="f1"),
            "fc_hash2": CacheData("fc_hash2", (1,), func_name="f1"),
            "fc_hash3": CacheData("fc_hash3", [False], func_name="f1"),
        }
        self.storage.get_cached_data_of_a_function = Mock(return_value=expected_data)

        data = self.function_retrieval.get_function_cache_entries(
            "f1", use_thread=use_thread
        )

        self.assertDictEqual(data, expected_data)
        self.assertListEqual(
            self.function_retrieval._functions_already_loaded_from_storage, ["f1"]
        )
        self.storage.get_cached_data_of_a_function.assert_called_once_with(
            "f1", use_isolated_connection=use_thread
        )

    def test_save_cache_data(self):
        self.storage.save_cache_data = Mock(return_value=None)
        conn = random.choice([True, False])
        data = {
            "fc_hash1": CacheData("fc_hash1", (1, 2, 3), func_name="f1"),
            "fc_hash2": CacheData("fc_hash2", True, func_name="f2"),
            "fc_hash3": CacheData("fc_hash3", -55.2, func_name="f3"),
        }
        expected_data = copy.deepcopy(data)

        self.function_retrieval.save_cache_data(data, use_isolated_connection=conn)

        self.storage.save_cache_data.assert_called_once_with(
            expected_data, use_isolated_connection=conn
        )


if __name__ == "__main__":
    unittest.main()
