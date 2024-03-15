from execute_exp.services.memory_architecures.AbstractOneDictMemArch import AbstractOneDictMemArch
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy
from execute_exp.services.storages.Storage import Storage
from entities.CacheData import CacheData

#TODO: TEST
class OneDictOneSetMemArch(AbstractOneDictMemArch):
    def __init__(self, storage:Storage, retrieval_strategy:AbstractRetrievalStrategy, use_threads:bool):
        super().__init__(storage, retrieval_strategy, use_threads)
        self.__NEW_DATA = set()
            
    def create_cache_entry(self, func_call_hash:str, func_return, func_name=None):
        data = CacheData(func_call_hash, func_return, func_name)
        self.__NEW_DATA.add(data)
        with self._DATA_DICTIONARY_SEMAPHORE:
            self._DATA_DICTIONARY[func_call_hash] = data
        
    def save_new_cache_entries(self):
        data = {e.func_call_hash:e for e in self.__NEW_DATA}
        self._storage.save_cache_data(data)
