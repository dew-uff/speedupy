from typing import Dict, Optional
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.storages.Storage import Storage

class AbstractRetrievalStrategy():
    def __init__(self, storage:Storage):
        self._storage = storage

    def get_initial_cache_entries(self, use_thread=False) -> Dict[str, CacheData]: return {}
    def get_cache_entry(self, func_call_hash:str, func_name=None) -> Optional[CacheData]: return
    def get_function_cache_entries(self, func_name:str, use_thread=False) -> Dict[str, CacheData]: return {}
    def save_cache_data(self, data:Dict[str, CacheData], use_isolated_connection=False) -> None:
        for cache_data in data.values(): cache_data.func_name = None
        self._storage.save_cache_data(data, use_isolated_connection=use_isolated_connection)