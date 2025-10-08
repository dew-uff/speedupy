import unittest, os, sys, random
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy
from execute_exp.services.memory_architecures.OneDictMemArch import OneDictMemArch
from execute_exp.entitites.CacheData import CacheData
from test.test_helpers import random_str


class TestOneDictMemArch(unittest.TestCase):
    def setUp(self):
        self.retrieval_strategy = Mock(AbstractRetrievalStrategy)
        self.use_threads = random.choice([True, False])
        self.mem_arch = OneDictMemArch(self.retrieval_strategy, self.use_threads)

    def test_create_cache_entry(self):
        fc_hash = random_str()
        func_return = random.choices([10, True, {2, 3}, (5,), {'k': 10}])
        func_name = random.choice([random_str(), None])

        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, {})

        self.mem_arch.create_cache_entry(fc_hash, func_return, func_name=func_name)

        self.assertDictEqual(self.mem_arch._DATA_DICTIONARY, {fc_hash: CacheData(fc_hash, func_return, func_name)})

    def test_save_new_cache_entries(self):
        fc_hash = random_str()
        func_return = random.choices([10, True, {2, 3}, (5,), {'k': 10}])
        func_name = random.choice([random_str(), None])
        self.mem_arch._DATA_DICTIONARY = random.choice([{}, {fc_hash: CacheData(fc_hash, func_return, func_name)}])

        self.mem_arch.save_new_cache_entries()

        self.retrieval_strategy.save_cache_data.assert_called_once_with(self.mem_arch._DATA_DICTIONARY)

    def test_get_new_cache_entries_size(self):
        self.mem_arch._DATA_DICTIONARY, expected_size = random.choice([[{}, 5],
                                                                       [{'fc_hash': CacheData('fc_hash', 10, 'func')}, 188],
                                                                       [{'fc_hash2': CacheData('fc_hash2', False, None)}, 182]])

        size = self.mem_arch.get_new_cache_entries_size()

        self.assertEqual(size, expected_size)


if __name__ == '__main__':
    unittest.main()
