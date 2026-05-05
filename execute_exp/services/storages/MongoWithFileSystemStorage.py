from typing import Dict, Optional

from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.Storage import Storage
from execute_exp.services.storages.MongoStorage import MongoStorage
from execute_exp.services.storages.FileSystemStorage import FileSystemStorage
from execute_exp.entitites.CacheData import CacheData
import pymongo


class MongoWithFileSystemStorage(Storage):
    def __init__(self, mongo_storage: MongoStorage, filesystem_storage: FileSystemStorage):
        super().__init__(None)
        self.mongo = mongo_storage
        self.filesystem = filesystem_storage

    def get_all_cached_data(self, use_isolated_connection=False) -> Dict[str, CacheData]:
        return {**self.mongo.get_all_cached_data(use_isolated_connection),
                **self.filesystem.get_all_cached_data(use_isolated_connection)}

    def get_cached_data_of_a_function(self, func_name: str, use_isolated_connection=False) -> Dict[str, CacheData]:
        return {**self.mongo.get_cached_data_of_a_function(func_name, use_isolated_connection),
                **self.filesystem.get_cached_data_of_a_function(func_name, use_isolated_connection)}

    def get_cached_data_of_a_function_call(self, func_call_hash: str, func_name=None, use_isolated_connection=False) -> Optional[CacheData]:
        cache = self.mongo.get_cached_data_of_a_function_call(func_call_hash, func_name, use_isolated_connection)
        if cache is not None: return cache

        return self.filesystem.get_cached_data_of_a_function_call(func_call_hash, func_name, use_isolated_connection)

    def save_cache_data(self, data: Dict[str, CacheData], use_isolated_connection=False) -> None:
        if len(data) == 0: return

        for func_call_hash, cache_data in data.items():
            try:
                self.mongo.save_cache_data({func_call_hash: cache_data}, use_isolated_connection)
            except (pymongo.errors.DocumentTooLarge, pymongo.errors.OperationFailure):
                self.filesystem.save_cache_data({func_call_hash: cache_data}, use_isolated_connection)
