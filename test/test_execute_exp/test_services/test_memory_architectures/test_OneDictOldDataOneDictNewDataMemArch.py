import unittest
from typing import Dict

from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.services.memory_architecures.OneDictOldDataOneDictNewDataMemArch import (
    OneDictOldDataOneDictNewDataMemArch,
)
from test_execute_exp.test_services.test_memory_architectures.AbstractTwoDictMemArchTest import (
    AbstractTwoDictMemArchTest,
)


class TestOneDictOldDataOneDictNewDataMemArch(
    AbstractTwoDictMemArchTest, unittest.TestCase
):
    def create_instance(self) -> AbstractMemArch:
        return OneDictOldDataOneDictNewDataMemArch(self.retrieval_strategy, False)

    def assert_cache_on_RAM_equal(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, persisted_data)
        self.assertDictEqual(self.mem_arch._NEW_DATA_DICTIONARY, non_persisted_data)

    def insert_data_on_cache_RAM(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        self.mem_arch._DATA_DICTIONARY.update(persisted_data)
        self.mem_arch._NEW_DATA_DICTIONARY.update(non_persisted_data)


if __name__ == "__main__":
    unittest.main()
