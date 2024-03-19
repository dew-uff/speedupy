from execute_exp.services.memory_architecures.AbstractOneDictMemArch import AbstractOneDictMemArch
from execute_exp.entitites.CacheData import CacheData

class OneDictMemArch(AbstractOneDictMemArch):
    def create_cache_entry(self, func_call_hash:str, func_return, func_name=None):
        with self._DATA_DICTIONARY_SEMAPHORE:
            self._DATA_DICTIONARY[func_call_hash] = CacheData(func_call_hash, func_return, func_name)
        
    def save_new_cache_entries(self):
        self._retrieval_strategy.save_cache_data(self._DATA_DICTIONARY)
