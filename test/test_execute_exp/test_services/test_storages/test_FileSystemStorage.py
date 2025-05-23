import unittest, os, sys

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.storages.FileSystemStorage import FileSystemStorage
from constantes import Constantes
from pickle import dumps
from typing import Dict
from execute_exp.entitites.CacheData import CacheData
from test_execute_exp.test_services.test_storages.AbstractStorageTest import AbstractStorageTest


# XXX: CONTINUAR REFATORAÇÃO
class TestFileSystemStorage(AbstractStorageTest, unittest.TestCase):
    def create_instance(self):
        os.makedirs(Constantes().CACHE_FOLDER_NAME)
        return FileSystemStorage(Constantes().CACHE_FOLDER_NAME)

    def assert_storage_is_empty(self):
        self.assertListEqual(os.listdir(Constantes().CACHE_FOLDER_NAME), [])







    

    # XXX: CORRIGIR PARA FORMATO DE AbstractStorageTest
    def assert_cache_data_correctly_inserted(self, func_call_hash, func_return, func_name=None):
        file_path = Constantes().CACHE_FOLDER_NAME
        if func_name:
            file_path = os.path.join(file_path, func_name, func_call_hash)
        else:
            file_path = os.path.join(file_path, func_call_hash)
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'rb') as f:
            self.assertEqual(f.read(), dumps(func_return))

    def assert_data_gotten_is_correct(self, data_gotten: Dict[str, CacheData], expected_data: Dict[str, CacheData]):
        self.assertSetEqual(set(data_gotten.keys()), set(expected_data.keys()))
        for func_call_hash in data_gotten:
            self.assert_two_cache_data_are_equal(data_gotten[func_call_hash],
                                                 expected_data[func_call_hash])

    def manually_cache_a_record_group_by_function_name(self, func_name, func_hash, func_return):
        folder_path = os.path.join(Constantes().CACHE_FOLDER_NAME, func_name)
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(func_name, func_hash)
        self.manually_cache_a_record(file_path, func_return)

    # XXX: COLOCAR NO FORMAT DE AbstractStorageTest
    def manually_cache_a_record(self, func_hash, func_return):
        file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, func_hash)
        with open(file_path, 'wb') as f:
            f.write(dumps(func_return))





 
 

 
 

    





















    # XXX: TALVEZ ESSE TESTE SÓ FAÇA SENTIDO PARA FileSystemStorage
    def test_save_cache_data_of_a_function_call_grouped_by_function_name_when_function_directory_doesnt_exist(self):
        file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, 'f1', 'func_call_hash')
        self.assertFalse(os.path.exists(file_path))

        self.storage._save_cache_data_of_a_function_call('func_call_hash', [3.1245123], func_name='f1')
        self.assert_cache_data_correctly_inserted('func_call_hash', [3.1245123], func_name='f1')

    # XXX: TALVEZ ESSE TESTE SÓ FAÇA SENTIDO PARA FileSystemStorage
    def test_save_cache_data_of_a_function_call_grouped_by_function_name_when_function_directory_already_exists(self):
        self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash', MyClass())

        self.storage._save_cache_data_of_a_function_call('func_call_hash', MyClass(), func_name='f1')
        self.assert_cache_data_correctly_inserted('func_call_hash', MyClass(), func_name='f1')
