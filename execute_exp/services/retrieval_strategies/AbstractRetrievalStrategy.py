from typing import Dict, Optional
from entities.CacheData import CacheData
from execute_exp.services.storages.Storage import Storage

#TODO: TEST
class AbstractRetrievalStrategy():
    def __init__(self, storage:Storage):
        self._storage = storage

    def get_initial_cache_entries(self, use_thread=False) -> Dict[str, CacheData]: return {}
    def get_cache_entry(self, func_call_hash:str) -> Optional[CacheData]: return
    def get_function_cache_entries(self, func_name:str, use_thread=False) -> Optional[Dict[str, CacheData]]: return