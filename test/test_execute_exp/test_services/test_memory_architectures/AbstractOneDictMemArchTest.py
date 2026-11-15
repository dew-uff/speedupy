import random
import time
import unittest
from unittest.mock import Mock

from test_helpers import random_str

from execute_exp.entitites.CacheData import CacheData
from test_execute_exp.test_services.test_memory_architectures.AbstractMemArchTest import (
    AbstractMemArchTest,
)


class AbstractOneDictMemArchTest(AbstractMemArchTest):
    def test_get_initial_cache_entries_using_a_thread_simulating_race_condition(self):
        records = {
            "func_call_hash1": CacheData("func_call_hash1", True),
            "func_call_hash2": CacheData("func_call_hash2", 10.123),
            "func_call_hash3": CacheData("func_call_hash3", {1, -3, "test"}),
        }
        self.retrieval_strategy.get_initial_cache_entries = Mock(return_value=records)
        self.mem_arch._use_threads = True
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.acquire()
        self.mem_arch.get_initial_cache_entries()

        time.sleep(0.2)
        self.retrieval_strategy.get_initial_cache_entries.assert_called_once()

        for i in range(
            5
        ):  # Checking that thread is waiting for the semaphore to be released
            self.assertTrue(self.mem_arch._thread.is_alive())
            self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, {})
            time.sleep(0.2)
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.release()

        while self.mem_arch._thread.is_alive():
            pass
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, records)

    def test_get_function_entries_from_storage_using_a_thread_simulating_race_condition(
        self,
    ):
        original_data = {
            "fc_hash0": CacheData("fc_hash0", True, func_name="f0"),
            "fc_hash00": CacheData("fc_hash00", False, func_name="f0"),
        }
        loaded_data = {
            "fc_hash1": CacheData("fc_hash1", (1, 2, 3), func_name="f1"),
            "fc_hash2": CacheData("fc_hash2", {1, 2, 3}, func_name="f1"),
        }
        self.mem_arch._DATA_DICTIONARY = original_data
        self.retrieval_strategy.get_function_cache_entries = Mock(
            return_value=loaded_data
        )
        self.retrieval_strategy.get_cache_entry = Mock(
            return_value=loaded_data["fc_hash1"]
        )
        self.mem_arch._use_threads = True
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.acquire()

        c = self.mem_arch.get_cache_entry("fc_hash1", "f1")

        time.sleep(0.2)

        self.assertTupleEqual(c, (1, 2, 3))
        self.retrieval_strategy.get_function_cache_entries.assert_called_once()
        self.retrieval_strategy.get_cache_entry.assert_called_once()

        for i in range(
            5
        ):  # Checking that thread is waiting for the semaphore to be released
            self.assertTrue(self.mem_arch._thread.is_alive())
            self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, original_data)
            time.sleep(0.2)
        self.mem_arch._DATA_DICTIONARY_SEMAPHORE.release()

        while self.mem_arch._thread.is_alive():
            pass

        loaded_data.update(original_data)
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, loaded_data)

    def test_create_cache_entry(self):
        persisted_data = {
            "fc_hash2": CacheData("fc_hash2", {1, 2, 3}),
            "fc_hash3": CacheData("fc_hash3", False),
        }
        self.insert_data_on_cache_RAM({}, persisted_data)

        fc_hash = random_str()
        func_return = random.choices([10, True, {2, 3}, (5,), {"k": 10}])
        func_name = random.choice([random_str(), None])
        self.mem_arch.create_cache_entry(fc_hash, func_return, func_name=func_name)

        non_persisted_data = {fc_hash: CacheData(fc_hash, func_return, func_name)}
        self.assert_cache_on_RAM_equal(non_persisted_data, persisted_data)

    def test_save_new_cache_entries(self):
        fc_hash = random_str()
        func_return = random.choices([10, True, {2, 3}, (5,), {"k": 10}])
        func_name = random.choice([random_str(), None])
        non_persisted_data = {fc_hash: CacheData(fc_hash, func_return, func_name)}
        self.insert_data_on_cache_RAM(non_persisted_data, {})

        self.mem_arch.save_new_cache_entries()

        self.retrieval_strategy.save_cache_data.assert_called_once_with(
            non_persisted_data
        )


# XXX : IMPLEMENTAR TESTE QUE CHAME FUNÇÃO PASSANDO FUNC_NAME DIFERENTE DE NULL, MAS O RETRIEVAL STRATEGY É LAZY OU EAGER

if __name__ == "__main__":
    unittest.main()
