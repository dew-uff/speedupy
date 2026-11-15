import os
import unittest
from typing import Dict

from constantes import Constantes
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.FileSystemStorage import FileSystemStorage
from execute_exp.services.storages.Storage import Storage
from test_execute_exp.test_services.test_storages.AbstractStorageTest import (
    AbstractStorageTest,
)


class TestFileSystemStorage(AbstractStorageTest, unittest.TestCase):
    def create_instance(self, serializer: Serializer) -> Storage:
        os.makedirs(Constantes().CACHE_FOLDER_NAME)
        storage = FileSystemStorage(serializer)
        storage.CACHE_FOLDER_NAME = Constantes().CACHE_FOLDER_NAME
        return storage

    def assert_storage_is_empty(self):
        self.assertListEqual(os.listdir(Constantes().CACHE_FOLDER_NAME), [])

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        data_gotten = {}
        content = os.listdir(Constantes().CACHE_FOLDER_NAME)

        if len(content) == 0 and len(expected_data) == 0:
            return

        if os.path.isdir(os.path.join(Constantes().CACHE_FOLDER_NAME, content[0])):
            for folder in content:
                files = os.listdir(os.path.join(Constantes().CACHE_FOLDER_NAME, folder))
                for filename in files:
                    file_path = os.path.join(
                        Constantes().CACHE_FOLDER_NAME, folder, filename
                    )
                    with open(file_path, "rb") as f:
                        output = self.serializer.load(f)
                    data_gotten[filename] = CacheData(filename, output, folder)
        else:
            for filename in content:
                file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, filename)
                with open(file_path, "rb") as f:
                    output = self.serializer.load(f)
                data_gotten[filename] = CacheData(filename, output)

        self.assert_data_gotten_is_correct(data_gotten, expected_data)

    def manually_cache_a_record(self, func_hash, func_return, func_name=None, **kwargs):
        folder_path = Constantes().CACHE_FOLDER_NAME
        if func_name:
            folder_path = os.path.join(folder_path, func_name)
            os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, func_hash)
        with open(file_path, "wb") as f:
            self.serializer.dump(func_return, f)
