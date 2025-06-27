import os
from typing import Dict, Optional

from constantes import Constantes
from execute_exp.services.storages.Storage import Storage
from execute_exp.entitites.CacheData import CacheData

from entities.BTree import DiskBTree


class BTreeFileSystemStorage(Storage):
    CACHE_FOLDER_NAME = Constantes().CACHE_FOLDER_NAME

    def __init__(self):
        self.btree = DiskBTree(os.path.join(self.CACHE_FOLDER_NAME, 'btree.dat'),
                               os.path.join(self.CACHE_FOLDER_NAME, 'btree.values'))

    def get_all_cached_data(self, use_isolated_connection=False) -> Dict[str, CacheData]: pass

    def get_cached_data_of_a_function(self, func_name: str, use_isolated_connection=False) -> Dict[str, CacheData]: pass

    # XXX: TESTAR
    def get_cached_data_of_a_function_call(self, func_call_hash: str, func_name=None, use_isolated_connection=False) -> Optional[CacheData]:
        if func_name: return None
        result = self.btree.search(func_call_hash)
        return CacheData(func_call_hash, result, func_name=func_name)

    # XXX: TESTAR
    def save_cache_data(self, data: Dict[str, CacheData], use_isolated_connection=False) -> None:
        for func_call_hash, cache_data in data.items():
            self._save_cache_data_of_a_function_call(func_call_hash,
                                                     cache_data.output,
                                                     func_name=cache_data.func_name)

    # XXX: TESTAR
    def _save_cache_data_of_a_function_call(self, func_call_hash: str, func_output, func_name=None) -> None:
        if func_name: return None
        self.btree.insert(func_call_hash, func_output)

    def __del__(self):
        self.btree.close()
