from execute_exp.memory_architectures.AbstractOneDictMemArch import AbstractOneDictMemArch
from execute_exp.memory_architectures.MemArchImpl import AbstractRetrievalStrategy
from execute_exp.services.storages.Storage import Storage
from entities.CacheData import CacheData

#TODO: TEST
class TwoDictMemArch(AbstractOneDictMemArch):
    def __init__(self, storage:Storage, retrieval_strategy:AbstractRetrievalStrategy, use_threads:bool):
        super().__init__(storage, retrieval_strategy, use_threads)
        self.__NEW_DATA_DICTIONARY = {}
    
    def _get_cache_entry_from_dict(self, func_call_hash:str):
        c = super()._get_cache_entry_from_dict(func_call_hash)
        if c: return c
        if(func_call_hash in self.__NEW_DATA_DICTIONARY):
            return self.__NEW_DATA_DICTIONARY[func_call_hash]
            
    def create_cache_entry(self, func_call_hash:str, func_return, func_name=None):
        self.__NEW_DATA_DICTIONARY[func_call_hash] = CacheData(func_call_hash, func_return, func_name)
        
    def save_new_cache_entries(self):
        self._storage.save_cache_data(self.__NEW_DATA_DICTIONARY)
