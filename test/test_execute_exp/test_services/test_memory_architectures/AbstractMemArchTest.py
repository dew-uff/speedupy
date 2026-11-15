from typing import Dict
import os, sys, time, threading
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split("test/")[0]
sys.path.append(project_folder)

from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import (
    AbstractRetrievalStrategy,
)
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.entitites.CacheData import CacheData


class AbstractMemArchTest(object):
    def setUp(self):
        self.retrieval_strategy = Mock(AbstractRetrievalStrategy)
        self.mem_arch = self.create_instance()

    def create_instance(self) -> AbstractMemArch:
        pass

    def assert_cache_on_RAM_equal(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        pass

    def insert_data_on_cache_RAM(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        pass

    def test_get_initial_cache_entries_when_retrieval_strategy_doesnt_load_records(
        self,
    ):
        self.retrieval_strategy.get_initial_cache_entries = Mock(return_value={})
        self.mem_arch.get_initial_cache_entries()

        self.retrieval_strategy.get_initial_cache_entries.assert_called_once()
        self.assert_cache_on_RAM_equal({}, {})

    def test_get_initial_cache_entries_when_some_records_are_loaded_from_storage(self):
        records = {
            "func_call_hash1": CacheData("func_call_hash1", True),
            "func_call_hash2": CacheData("func_call_hash2", 10.123),
            "func_call_hash3": CacheData("func_call_hash3", {1, -3, "test"}),
        }
        self.retrieval_strategy.get_initial_cache_entries = Mock(return_value=records)
        self.mem_arch.get_initial_cache_entries()

        self.retrieval_strategy.get_initial_cache_entries.assert_called_once()
        self.assert_cache_on_RAM_equal({}, records)

    def test_get_initial_cache_entries_using_a_thread(self):
        records = {
            "func_call_hash1": CacheData("func_call_hash1", True),
            "func_call_hash2": CacheData("func_call_hash2", 10.123),
            "func_call_hash3": CacheData("func_call_hash3", {1, -3, "test"}),
        }
        self.retrieval_strategy.get_initial_cache_entries = Mock(return_value=records)
        self.mem_arch._use_threads = True
        self.mem_arch.get_initial_cache_entries()

        while self.mem_arch._thread.is_alive():
            pass
        self.retrieval_strategy.get_initial_cache_entries.assert_called_once()
        self.assert_cache_on_RAM_equal({}, records)

    def test_get_cache_entry_when_cache_miss_but_all_function_data_is_loaded_to_RAM(
        self,
    ):
        function_data = {
            "fc_hash1": CacheData("fc_hash1", (1, 2, 3), func_name="f1"),
            "fc_hash2": CacheData("fc_hash2", {1, 2, 3}, func_name="f1"),
        }
        self.retrieval_strategy.get_function_cache_entries = Mock(
            return_value=function_data
        )
        self.retrieval_strategy.get_cache_entry = Mock(return_value=None)

        c = self.mem_arch.get_cache_entry("func_call_hash")

        self.assertIsNone(c)
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.retrieval_strategy.get_cache_entry.assert_called_once()
        self.assert_cache_on_RAM_equal({}, function_data)

    def test_get_cache_entry_when_cache_hit_because_data_is_already_on_RAM(self):
        original_data = {
            "fc_hash1": CacheData("fc_hash1", 10),
            "fc_hash2": CacheData("fc_hash2", "test"),
            "fc_hash3": CacheData("fc_hash3", False),
        }
        self.insert_data_on_cache_RAM({}, original_data)

        c = self.mem_arch.get_cache_entry("fc_hash2")

        self.assertEqual(c, original_data["fc_hash2"].output)
        self.retrieval_strategy.get_function_cache_entries.assert_not_called()
        self.retrieval_strategy.get_cache_entry.assert_not_called()
        self.assert_cache_on_RAM_equal({}, original_data)

    def test_get_cache_entry_when_cache_hit_because_all_function_data_is_retrieved_from_storage(
        self,
    ):
        original_data = {"fc_hash3": CacheData("fc_hash3", False, func_name="f3")}
        function_data = {
            "fc_hash1": CacheData("fc_hash1", (1, 2, 3), func_name="f1"),
            "fc_hash2": CacheData("fc_hash2", {1, 2, 3}, func_name="f1"),
        }
        self.insert_data_on_cache_RAM({}, original_data)
        self.retrieval_strategy.get_function_cache_entries = Mock(
            return_value=function_data
        )
        self.retrieval_strategy.get_cache_entry = Mock(
            return_value=function_data["fc_hash1"]
        )

        c = self.mem_arch.get_cache_entry("fc_hash1")

        self.assertEqual(c, function_data["fc_hash1"].output)
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.retrieval_strategy.get_cache_entry.assert_not_called()
        self.assert_cache_on_RAM_equal({}, original_data | function_data)

    def test_get_cache_entry_when_cache_hit_because_a_function_call_data_is_retrieved_from_storage(
        self,
    ):
        original_data = {
            "fc_hash2": CacheData("fc_hash2", {1, 2, 3}),
            "fc_hash3": CacheData("fc_hash3", False),
        }
        cache_data = CacheData("fc_hash1", (1, 2, 3))
        self.insert_data_on_cache_RAM({}, original_data)
        self.retrieval_strategy.get_function_cache_entries = Mock(return_value={})
        self.retrieval_strategy.get_cache_entry = Mock(return_value=cache_data)

        c = self.mem_arch.get_cache_entry("fc_hash1")

        self.assertEqual(c, cache_data.output)
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.retrieval_strategy.get_cache_entry.assert_called_once()
        self.assert_cache_on_RAM_equal({}, original_data | {"fc_hash1": cache_data})

    def test_get_cache_entry_when_function_data_is_being_loaded_in_a_thread_with_the_requested_data(
        self,
    ):
        def fill_dict():
            time.sleep(0.2)
            start = time.perf_counter()
            end = time.perf_counter()
            i = 0
            while (end - start) < 1:
                self.insert_data_on_cache_RAM(
                    {}, {f"fc_hash{i}": CacheData(f"fc_hash{i}", i)}
                )
                end = time.perf_counter()
                i += 1

        self.retrieval_strategy.get_function_cache_entries = Mock(return_value={})
        self.retrieval_strategy.get_cache_entry = Mock(return_value=None)

        t = threading.Thread(target=fill_dict)
        t.start()
        aux1, aux2 = 0, 0
        while t.is_alive():
            c = self.mem_arch.get_cache_entry("fc_hash100")
            try:
                self.assertIsNone(c)
                aux1 += 1
            except AssertionError:
                self.assertEqual(c, 100)
                aux2 += 1
        self.assertTrue(aux1 > 0)
        self.assertTrue(aux2 > 0)

    # INFO: The unit tests for the following methods must be implemented by each subclass!
    # INFO:    def create_cache_entry(self, func_call_hash: str, func_return, func_name=None) -> None: pass
    # INFO:    def save_new_cache_entries(self) -> None: return
    # INFO:    def get_new_cache_entries_size(self) -> int: return 0
