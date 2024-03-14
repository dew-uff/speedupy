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
#TODO: ADICIONAR self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB = []
    # self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(func_name)
class FunctionRetrieval(AbstractRetrievalStrategy):
    def get_cache_entry(self, func_call_hash:str) -> Optional[CacheData]:
        return self._storage.get_cached_data_of_a_function_call(func_call_hash)
    
    def get_function_cache_entries(self, func_name:str, use_thread=False) -> Optional[Dict[str, CacheData]]:
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

#TODO: TEST
class ZeroDictMemArch(AbstractMemArch):
    #This MemoryArchitecture can only be used with LazyRetrieval because it saves no data on RAM! Thus, it always runs sequentially!
    def __init__(self, storage:Storage, retrieval_strategy:AbstractRetrievalStrategy, use_threads:bool):
        super().__init__(storage)
        self._retrieval_strategy = retrieval_strategy
        self._use_threads = use_threads

    def get_initial_cache_entries(self): return
    
    def get_cache_entry(self, func_call_hash:str):
        try: return self._retrieval_strategy.get_cache_entry(func_call_hash).output
        except AttributeError: return
    
    def create_cache_entry(self, func_call_hash:str, func_return, func_name=None):
        data = CacheData(func_call_hash, func_return, func_name)
        self._storage.save_cache_data({func_call_hash: data})
        
    def save_new_cache_entries(self): return

import threading

#TODO: TEST
#TODO: TEST IF I CAN READ DICTIONARY WITHOUT SEMAPHORE
class OneDictMemArch(AbstractMemArch):
    def __init__(self, storage:Storage, retrieval_strategy:AbstractRetrievalStrategy, use_threads:bool):
        super().__init__(storage)
        self._retrieval_strategy = retrieval_strategy
        self._use_threads = use_threads

        self.__DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()
        self.__DATA_DICTIONARY = {}

    def get_initial_cache_entries(self):
        def populate_cached_data_dictionary():
            data = self._retrieval_strategy.get_initial_cache_entries(use_thread=self._use_threads)
            with self.__DATA_DICTIONARY_SEMAPHORE:
                self.__DATA_DICTIONARY = data

        if self._use_threads:
            threading.Thread(target=populate_cached_data_dictionary).start()
        else:
            populate_cached_data_dictionary()
    
    def get_cache_entry(self, func_call_hash:str, func_name=None):
        def update_DATA_DICTIONARY():
            data = self._retrieval_strategy.get_function_cache_entries(func_name,
                                                                       use_thread=self._use_threads)
            with self.__DATA_DICTIONARY_SEMAPHORE:
                self.__DATA_DICTIONARY.update(data)

        with self.__DATA_DICTIONARY_SEMAPHORE:
            if(func_call_hash in self.__DATA_DICTIONARY):
                return self.__DATA_DICTIONARY[func_call_hash]
    
        if func_name:
            if self._use_threads:
                threading.Thread(target=update_DATA_DICTIONARY).start()
                c = self._retrieval_strategy.get_cache_entry(func_call_hash)
                if c: return c.output
            else:
                update_DATA_DICTIONARY()
                if(func_call_hash in self.__DATA_DICTIONARY):
                    return self.__DATA_DICTIONARY[func_call_hash].output
        else:
            c = self._retrieval_strategy.get_cache_entry(func_call_hash)
            if c:
                self.__DATA_DICTIONARY[c.function_call_hash] = c
                return c.output
            
    def create_cache_entry(self, func_call_hash:str, func_return, func_name=None):
        with self.__DATA_DICTIONARY_SEMAPHORE:
            self.__DATA_DICTIONARY[func_call_hash] = CacheData(func_call_hash, func_return, func_name)
        
    def save_new_cache_entries(self):
        self._storage.save_cache_data(self.__DATA_DICTIONARY)

class OneDictOneSetMemArch(AbstractMemArch): pass
class TwoDictMemArch(AbstractMemArch): pass

