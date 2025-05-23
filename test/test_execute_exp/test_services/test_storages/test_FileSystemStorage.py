import unittest, os, sys

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.storages.FileSystemStorage import FileSystemStorage
from execute_exp.services.storages.Storage import Storage
from constantes import Constantes
from pickle import dump, load
from typing import Dict
from execute_exp.entitites.CacheData import CacheData
from test_execute_exp.test_services.test_storages.AbstractStorageTest import AbstractStorageTest, MyClass


# XXX: CONTINUAR REFATORAÇÃO
class TestFileSystemStorage(AbstractStorageTest, unittest.TestCase):
    def create_instance(self) -> Storage:
        os.makedirs(Constantes().CACHE_FOLDER_NAME)
        return FileSystemStorage(Constantes().CACHE_FOLDER_NAME)

    def assert_storage_is_empty(self):
        self.assertListEqual(os.listdir(Constantes().CACHE_FOLDER_NAME), [])

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        data_gotten = {}
        content = os.listdir(Constantes().CACHE_FOLDER_NAME)

        if len(content) == 0 and len(expected_data) == 0: return

        if os.path.isdir(os.path.join(Constantes().CACHE_FOLDER_NAME, content[0])):
            for folder in content:
                files = os.listdir(os.path.join(Constantes().CACHE_FOLDER_NAME, folder))
                for filename in files:
                    file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, folder, filename)
                    with open(file_path, 'rb') as f: output = load(f)
                    data_gotten[filename] = CacheData(filename, output, folder)
        else:
            for filename in content:
                file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, filename)
                with open(file_path, 'rb') as f: output = load(f)
                data_gotten[filename] = CacheData(filename, output)

        self.assert_data_gotten_is_correct(data_gotten, expected_data)

    def manually_cache_a_record(self, func_hash, func_return, func_name=None, commit=False):
        folder_path = Constantes().CACHE_FOLDER_NAME
        if func_name:
            folder_path = os.path.join(folder_path, func_name)
            os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, func_hash)
        with open(file_path, 'wb') as f: dump(func_return, f)

    # XXX: TALVEZ ESSE TESTE SÓ FAÇA SENTIDO PARA FileSystemStorage
    def test_save_cache_data_of_a_function_call_grouped_by_function_name_when_function_directory_doesnt_exist(self):
        file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, 'f1', 'func_call_hash')
        self.assertFalse(os.path.exists(file_path))

        self.storage._save_cache_data_of_a_function_call('func_call_hash', [3.1245123], func_name='f1')
        self.assert_cached_data({'func_call_hash': CacheData('func_call_hash', [3.1245123], func_name='f1')})

    # XXX: TALVEZ ESSE TESTE SÓ FAÇA SENTIDO PARA FileSystemStorage
    def test_save_cache_data_of_a_function_call_grouped_by_function_name_when_function_directory_already_exists(self):
        self.manually_cache_a_record('func_call_hash', MyClass(), func_name='f1')

        self.storage._save_cache_data_of_a_function_call('func_call_hash', MyClass(), func_name='f1')
        self.assert_cached_data({'func_call_hash': CacheData('func_call_hash', MyClass(), func_name='f1')})
