import unittest, os, sys

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.storages.FileSystemStorage import FileSystemStorage
from constantes import Constantes
from pickle import dumps
from typing import Dict
from execute_exp.entitites.CacheData import CacheData

class TestFileSystemStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Constantes().CACHE_FOLDER_NAME = '.speedupy_test/cache/'
        os.makedirs(Constantes().CACHE_FOLDER_NAME)
        cls.storage = FileSystemStorage(Constantes().CACHE_FOLDER_NAME)
    
    @classmethod
    def tearDownClass(cls):
        os.system('rm -rf .speedupy_test/')
    
    def tearDown(self):
        os.system(f'rm -rf {Constantes().CACHE_FOLDER_NAME}/*')

    def manually_cache_a_record_group_by_function_name(self, func_name, func_hash, func_return):
        folder_path = os.path.join(Constantes().CACHE_FOLDER_NAME, func_name)
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(func_name, func_hash)
        self.manually_cache_a_record(file_path, func_return)

    def manually_cache_a_record(self, func_hash, func_return):
        file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, func_hash)
        with open(file_path, 'wb') as f:
            f.write(dumps(func_return))

    def assert_cache_data_correctly_inserted(self, func_call_hash, func_return, func_name=None):
        file_path = Constantes().CACHE_FOLDER_NAME
        if func_name:
            file_path = os.path.join(file_path, func_name, func_call_hash)
        else:
            file_path = os.path.join(file_path, func_call_hash)
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'rb') as f:
            self.assertEqual(f.read(), dumps(func_return))

    def assert_data_gotten_is_correct(self, data_gotten:Dict[str, CacheData], expected_data:Dict[str, CacheData]):
        self.assertSetEqual(set(data_gotten.keys()), set(expected_data.keys()))
        for func_call_hash in data_gotten:
            self.assert_two_cache_data_are_equal(data_gotten[func_call_hash],
                                                 expected_data[func_call_hash])
    
    def assert_two_cache_data_are_equal(self, cache_data_1:CacheData, cache_data_2:CacheData):
        self.assertEqual(cache_data_1.function_call_hash, cache_data_2.function_call_hash)
        self.assertEqual(cache_data_1.func_name, cache_data_2.func_name)
        self.assertEqual(dumps(cache_data_1.output), dumps(cache_data_2.output))

    def test_get_all_cached_data_when_there_is_no_cached_data(self):
        dicio = self.storage.get_all_cached_data()
        self.assertDictEqual(dicio, {})

    def test_get_all_cached_data_when_there_is_one_cached_data_record(self):
        self.manually_cache_a_record('func_call_hash', {1, 2, 5})

        dicio = self.storage.get_all_cached_data()

        expected_data = {'func_call_hash':CacheData('func_call_hash', {1, 2, 5})}
        self.assert_data_gotten_is_correct(dicio, expected_data)

    def test_get_all_cached_data_when_cached_data_record_is_an_instance_of_a_class(self):
        self.manually_cache_a_record('func_call_hash', MyClass())

        dicio = self.storage.get_all_cached_data()

        expected_data = {'func_call_hash':CacheData('func_call_hash', MyClass())}
        self.assert_data_gotten_is_correct(dicio, expected_data)

    def test_get_all_cached_data_when_there_are_many_cached_data_records(self):
        self.manually_cache_a_record('func_call_hash1', (True, 2, 5))
        self.manually_cache_a_record('func_call_hash2', [{'key1': 10, 'key_2': False}])
        self.manually_cache_a_record('func_call_hash3', -123.213)
        self.manually_cache_a_record('func_call_hash4', [1, 2.213, 'test'])

        dicio = self.storage.get_all_cached_data()

        expected_data = {'func_call_hash1':CacheData('func_call_hash1', (True, 2, 5)),
                         'func_call_hash2':CacheData('func_call_hash2', [{'key1': 10, 'key_2': False}]),
                         'func_call_hash3':CacheData('func_call_hash3', -123.213),
                         'func_call_hash4':CacheData('func_call_hash4', [1, 2.213, 'test'])}
        self.assert_data_gotten_is_correct(dicio, expected_data)
    
    def test_get_cached_data_of_a_function_when_there_is_no_cached_data(self):
        dicio = self.storage.get_cached_data_of_a_function('f1')
        self.assertDictEqual(dicio, {})

    def test_get_cached_data_of_a_function_when_there_is_cached_data_only_for_other_functions(self):
        self.manually_cache_a_record_group_by_function_name('f2', 'func_call_hash1', (True, 2, 5))
        self.manually_cache_a_record_group_by_function_name('f2', 'func_call_hash2', [{'key1': 10,
                                                                                  'key_2': False}])
        self.manually_cache_a_record_group_by_function_name('f3', 'func_call_hash3', -123.213)
        
        dicio = self.storage.get_cached_data_of_a_function('f1')
        self.assertDictEqual(dicio, {})

    def test_get_cached_data_of_a_function_when_there_is_cached_data_for_it_and_for_other_functions_too(self):
        self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash1', 5000.00)
        self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash11', (True, 2, 5))
        self.manually_cache_a_record_group_by_function_name('f2', 'func_call_hash2', [{'key1': 10,
                                                                                  'key_2': False}])
        self.manually_cache_a_record_group_by_function_name('f3', 'func_call_hash3', -123.213)
        
        dicio = self.storage.get_cached_data_of_a_function('f1')

        expected_data = {'func_call_hash1':CacheData('func_call_hash1', 5000.00, func_name='f1'),
                         'func_call_hash11':CacheData('func_call_hash11', (True, 2, 5), func_name='f1')}
        self.assert_data_gotten_is_correct(dicio, expected_data)

    def test_get_cached_data_of_a_function_when_there_is_a_cached_data_record_for_it(self):
        self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash1', [5, 'test', -2.8])
        
        dicio = self.storage.get_cached_data_of_a_function('f1')

        expected_data = {'func_call_hash1':CacheData('func_call_hash1', [5, 'test', -2.8], func_name='f1')}
        self.assert_data_gotten_is_correct(dicio, expected_data)
        
    def test_get_cached_data_of_a_function_when_there_are_many_cached_data_records_for_it(self):
        self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash1', 'testing')
        self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash2', (1,))
        self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash3', [10, -4, False])
        self.manually_cache_a_record_group_by_function_name('f3', 'func_call_hash4', -123.213)
        
        dicio = self.storage.get_cached_data_of_a_function('f1')

        expected_data = {'func_call_hash1':CacheData('func_call_hash1', 'testing', func_name='f1'),
                         'func_call_hash2':CacheData('func_call_hash2', (1,), func_name='f1'),
                         'func_call_hash3':CacheData('func_call_hash3', [10, -4, False], func_name='f1')}
        self.assert_data_gotten_is_correct(dicio, expected_data)
    
    def test_get_cached_data_of_a_function_call_when_this_record_doesnt_exist(self):
        cache_data = self.storage.get_cached_data_of_a_function_call('func_call_hash')
        self.assertIsNone(cache_data)

    def test_get_cached_data_of_a_function_call_when_this_record_exists(self):
        self.manually_cache_a_record('func_call_hash', (True, 2, 5))

        cache_data = self.storage.get_cached_data_of_a_function_call('func_call_hash')
        self.assert_two_cache_data_are_equal(cache_data, CacheData('func_call_hash', (True, 2, 5)))

    def test_get_cached_data_of_a_function_call_when_this_record_doesnt_exist_and_records_are_grouped_by_function_name(self):
        cache_data = self.storage.get_cached_data_of_a_function_call('func_call_hash', func_name='f1')
        self.assertIsNone(cache_data)

    def test_get_cached_data_of_a_function_call_when_this_record_exists_and_records_are_grouped_by_function_name(self):
        self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash', 'my_string')

        cache_data = self.storage.get_cached_data_of_a_function_call('func_call_hash', func_name='f1')
        self.assert_two_cache_data_are_equal(cache_data, CacheData('func_call_hash', 'my_string', func_name='f1'))

    def test_get_cached_data_of_a_function_call_when_this_record_doesnt_exists_but_other_records_exist(self):
        self.manually_cache_a_record('func_call_hash1', (True, 2, 5))
        self.manually_cache_a_record('func_call_hash2', -12.2131)
        self.manually_cache_a_record('func_call_hash3', False)

        cache_data = self.storage.get_cached_data_of_a_function_call('func_call_hash')
        self.assertIsNone(cache_data)
    
    def test_save_cache_data_of_a_function_call_when_function_call_record_doesnt_exist(self):
        file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, 'func_call_hash')
        self.assertFalse(os.path.exists(file_path))

        self.storage._save_cache_data_of_a_function_call('func_call_hash', False)
        self.assert_cache_data_correctly_inserted('func_call_hash', False)

    def test_save_cache_data_of_a_function_call_when_function_call_record_already_exists(self):
        self.manually_cache_a_record('func_call_hash', (True, 2, 5))

        self.storage._save_cache_data_of_a_function_call('func_call_hash', (True, 2, 5))
        self.assert_cache_data_correctly_inserted('func_call_hash', (True, 2, 5))

    def test_save_cache_data_of_a_function_call_grouped_by_function_name_when_function_directory_doesnt_exist(self):
        file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, 'f1', 'func_call_hash')
        self.assertFalse(os.path.exists(file_path))

        self.storage._save_cache_data_of_a_function_call('func_call_hash', [3.1245123], func_name='f1')
        self.assert_cache_data_correctly_inserted('func_call_hash', [3.1245123], func_name='f1')

    def test_save_cache_data_of_a_function_call_grouped_by_function_name_when_function_directory_already_exists(self):
        self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash', MyClass())

        self.storage._save_cache_data_of_a_function_call('func_call_hash', MyClass(), func_name='f1')
        self.assert_cache_data_correctly_inserted('func_call_hash', MyClass(), func_name='f1')

class MyClass():
    def __init__(self):
        self.__x = 10
        self.__y = 20