import unittest, os, sys, random

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.entitites.CacheData import CacheData
from test_execute_exp.test_services.test_memory_architectures.AbstractOneDictMemArchTest import AbstractOneDictMemArchTest


class AbstractTwoDictMemArchTest(AbstractOneDictMemArchTest):
    def test_get_new_cache_entries_size(self):
        self.mem_arch._NEW_DATA_DICTIONARY, expected_size = random.choice([[{}, 5],
                                                                          [{'fc_hash': CacheData('fc_hash', 10, 'func')}, 188],
                                                                          [{'fc_hash2': CacheData('fc_hash2', False, None)}, 182]])

        size = self.mem_arch.get_new_cache_entries_size()

        self.assertEqual(size, expected_size)


if __name__ == '__main__':
    unittest.main()
