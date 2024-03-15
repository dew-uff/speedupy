import threading
from execute_exp.services.storages.Storage import Storage
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch

#TODO: TEST
class AbstractOneDictMemArch(AbstractMemArch):
    def __init__(self, storage:Storage, retrieval_strategy:AbstractRetrievalStrategy, use_threads:bool):
        super().__init__(storage, retrieval_strategy, use_threads)
        self._DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()
        self._DATA_DICTIONARY = {}

    def get_initial_cache_entries(self):
        def populate_cached_data_dictionary():
            data = self._retrieval_strategy.get_initial_cache_entries(use_thread=self._use_threads)
            with self._DATA_DICTIONARY_SEMAPHORE:
                self._DATA_DICTIONARY = data

        if self._use_threads:
            threading.Thread(target=populate_cached_data_dictionary).start()
        else:
            populate_cached_data_dictionary()
    
    def _get_cache_entry_from_dict(self, func_call_hash:str):
        with self._DATA_DICTIONARY_SEMAPHORE:
            if(func_call_hash in self._DATA_DICTIONARY):
                return self._DATA_DICTIONARY[func_call_hash]

    def get_cache_entry(self, func_call_hash:str, func_name=None):
        def update_DATA_DICTIONARY():
            data = self._retrieval_strategy.get_function_cache_entries(func_name,
                                                                       use_thread=self._use_threads)
            with self._DATA_DICTIONARY_SEMAPHORE:
                self._DATA_DICTIONARY.update(data)

        c = self._get_cache_entry_from_dict()
        if c: return c.output
    
        if func_name:
            if self._use_threads:
                threading.Thread(target=update_DATA_DICTIONARY).start()
                c = self._retrieval_strategy.get_cache_entry(func_call_hash)
                if c: return c.output
            else:
                update_DATA_DICTIONARY()
                if(func_call_hash in self._DATA_DICTIONARY):
                    return self._DATA_DICTIONARY[func_call_hash].output
        else:
            c = self._retrieval_strategy.get_cache_entry(func_call_hash)
            if c:
                self._DATA_DICTIONARY[c.function_call_hash] = c
                return c.output