import random
import unittest
from typing import Dict

from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.services.memory_architecures.OneDictMemArch import OneDictMemArch
from test_execute_exp.test_services.test_memory_architectures.AbstractOneDictMemArchTest import (
    AbstractOneDictMemArchTest,
)


class TestOneDictMemArch(AbstractOneDictMemArchTest, unittest.TestCase):
    def create_instance(self) -> AbstractMemArch:
        return OneDictMemArch(self.retrieval_strategy, False)

    def assert_cache_on_RAM_equal(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        cache_data = non_persisted_data | persisted_data
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, cache_data)

    def insert_data_on_cache_RAM(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        cache_data = non_persisted_data | persisted_data
        self.mem_arch._DATA_DICTIONARY.update(cache_data)

    def test_get_new_cache_entries_size(self):
        self.mem_arch._DATA_DICTIONARY, expected_size = random.choice(
            [
                [{}, 5],
                [{"fc_hash": CacheData("fc_hash", 10, "func")}, 188],
                [{"fc_hash2": CacheData("fc_hash2", False, None)}, 182],
            ]
        )

        size = self.mem_arch.get_new_cache_entries_size()

        self.assertEqual(size, expected_size)


if __name__ == "__main__":
    unittest.main()
