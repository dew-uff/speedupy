from typing import Dict, Optional
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.storages.Storage import Storage
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy

class FunctionRetrieval(AbstractRetrievalStrategy):
    def __init__(self, storage:Storage):
        super().__init__(storage)
        self.__functions_already_loaded_from_storage = []

    def get_cache_entry(self, func_call_hash:str, func_name=None) -> Optional[CacheData]:
        return self._storage.get_cached_data_of_a_function_call(func_call_hash, func_name)
    
    def get_function_cache_entries(self, func_name:str, use_thread=False) -> Dict[str, CacheData]:
        if func_name in self.__functions_already_loaded_from_storage: return {}
        self.__functions_already_loaded_from_storage.append(func_name)
        return self._storage.get_cached_data_of_a_function(func_name,
                                                           use_isolated_connection=use_thread)
    
    def save_cache_data(self, data:Dict[str, CacheData], use_isolated_connection=False) -> None:
        self._storage.save_cache_data(data, use_isolated_connection=use_isolated_connection)
