from typing import Optional
import threading
from execute_exp.services.storages.Storage import Storage
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from entities.CacheData import CacheData

class AbstractOneDictMemArch(AbstractMemArch):
    def __init__(self, storage:Storage, retrieval_strategy:AbstractRetrievalStrategy, use_threads:bool):
        super().__init__(storage, retrieval_strategy, use_threads)
        self._DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()
        self._DATA_DICTIONARY = {}
        self._thread = None #Needed for unit testing!

    def get_initial_cache_entries(self) -> None:
        def populate_cached_data_dictionary():
            data = self._retrieval_strategy.get_initial_cache_entries(use_thread=self._use_threads)
            with self._DATA_DICTIONARY_SEMAPHORE:
                self._DATA_DICTIONARY = data

        if self._use_threads:
            self._thread = threading.Thread(target=populate_cached_data_dictionary)
            self._thread.start()
        else:
            populate_cached_data_dictionary()
    
    def get_cache_entry(self, func_call_hash:str, func_name=None):
        try:
            c = self._get_cache_entry_from_dict()
            if c is None:
                c = self._get_cache_entry_from_storage(func_call_hash, func_name)
            return c.output
        except AttributeError: return
            
    def _get_cache_entry_from_dict(self, func_call_hash:str) -> Optional[CacheData]:
        try:return self._DATA_DICTIONARY[func_call_hash]
        except KeyError: return

    def _get_cache_entry_from_storage(self, func_call_hash:str, func_name=None) -> Optional[CacheData]:
        try:
            if func_name:
                c = self._get_function_entries_from_storage(func_call_hash, func_name)
            else:
                #In this case, RetrievalStrategy is always Lazy, so we garantee there will not be a thread executing in parallel!
                c = self._retrieval_strategy.get_cache_entry(func_call_hash)
                self._DATA_DICTIONARY[c.function_call_hash] = c
            return c
        except AttributeError: return

    def _get_function_entries_from_storage(self, func_call_hash:str, func_name:str) -> Optional[CacheData]:
        def update_DATA_DICTIONARY():
            data = self._retrieval_strategy.get_function_cache_entries(func_name,
                                                                       use_thread=self._use_threads)
            with self._DATA_DICTIONARY_SEMAPHORE:
                self._DATA_DICTIONARY.update(data)

        try:
            if self._use_threads:
                self._thread = threading.Thread(target=update_DATA_DICTIONARY)
                self._thread.start()
                c = self._retrieval_strategy.get_cache_entry(func_call_hash)
            else:
                update_DATA_DICTIONARY()
                c = self._DATA_DICTIONARY[func_call_hash]
            return c
        except KeyError: return

    def create_cache_entry(self, func_call_hash:str, func_return, func_name=None) -> None: pass # Implemented by each subclass!
    def save_new_cache_entries(self): pass # Implemented by each subclass!
