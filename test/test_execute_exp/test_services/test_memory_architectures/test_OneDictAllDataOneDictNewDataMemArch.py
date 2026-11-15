import os
import sys
import unittest
from typing import Dict

project_folder = os.path.realpath(__file__).split("test/")[0]
sys.path.append(project_folder)

from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.services.memory_architecures.OneDictAllDataOneDictNewDataMemArch import (
    OneDictAllDataOneDictNewDataMemArch,
)
from test_execute_exp.test_services.test_memory_architectures.AbstractTwoDictMemArchTest import (
    AbstractTwoDictMemArchTest,
)


class TestOneDictAllDataOneDictNewDataMemArch(
    AbstractTwoDictMemArchTest, unittest.TestCase
):
    def create_instance(self) -> AbstractMemArch:
        return OneDictAllDataOneDictNewDataMemArch(self.retrieval_strategy, False)

    def assert_cache_on_RAM_equal(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        self.assertDictEqual(
            self.mem_arch._DATA_DICTIONARY, non_persisted_data | persisted_data
        )
        self.assertDictEqual(self.mem_arch._NEW_DATA_DICTIONARY, non_persisted_data)

    def insert_data_on_cache_RAM(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        self.mem_arch._DATA_DICTIONARY.update(non_persisted_data | persisted_data)
        self.mem_arch._NEW_DATA_DICTIONARY.update(non_persisted_data)


if __name__ == "__main__":
    unittest.main()
