from typing import Dict, Optional
from entities.CacheData import CacheData
from execute_exp.services.storages.Storage import Storage
from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch

#TODO: TEST
class AbstractRetrievalStrategy():
    def __init__(self, storage:Storage):
        self._storage = storage

    def get_initial_cache_entries(self, use_thread=False) -> Dict[str, CacheData]: return {}
    def get_cache_entry(self, func_call_hash:str) -> Optional[CacheData]: return
    def get_function_cache_entries(self, func_name:str, use_thread=False) -> Optional[Dict[str, CacheData]]: return

#TODO: TEST
class LazyRetrieval(AbstractRetrievalStrategy):
    def get_cache_entry(self, func_call_hash:str) -> Optional[CacheData]:
        return self._storage.get_cached_data_of_a_function_call(func_call_hash)

#TODO: TEST
class FunctionRetrieval(AbstractRetrievalStrategy):
    def __init__(self, storage:Storage):
        super().__init__(storage)
        self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB = []

    def get_cache_entry(self, func_call_hash:str) -> Optional[CacheData]:
        return self._storage.get_cached_data_of_a_function_call(func_call_hash)
    
    def get_function_cache_entries(self, func_name:str, use_thread=False) -> Optional[Dict[str, CacheData]]:
        if func_name in self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB: return
        self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(func_name)
        return self._storage.get_cached_data_of_a_function(func_name,
                                                           use_isolated_connection=use_thread)

#TODO: TEST
class EagerRetrieval(AbstractRetrievalStrategy):
    def get_initial_cache_entries(self, use_thread=False) -> Dict[str, CacheData]:
        return self._storage.get_all_cached_data(use_isolated_connection=use_thread)






# class AbstractMemArch():
#     def __init__(self, storage:Storage):
#         self._storage = storage

#     def get_initial_cache_entries(self): pass
#     def get_cache_entry(self, func_call_hash:str, *args): pass
#     def create_cache_entry(self, func_call_hash:str, func_return, *args): pass
#     def save_new_cache_entries(self): pass

