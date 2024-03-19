from execute_exp.services.memory_architecures.AbstractOneDictMemArch import AbstractOneDictMemArch
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy
from execute_exp.entitites.CacheData import CacheData

class AbstractTwoDictMemArch(AbstractOneDictMemArch):
    def __init__(self, retrieval_strategy:AbstractRetrievalStrategy, use_threads:bool):
        super().__init__(retrieval_strategy, use_threads)
        self._NEW_DATA_DICTIONARY = {}

    def create_cache_entry(self, func_call_hash:str, func_return, func_name=None):
        self._NEW_DATA_DICTIONARY[func_call_hash] = CacheData(func_call_hash, func_return, func_name)
        
    def save_new_cache_entries(self):
        self._retrieval_strategy.save_cache_data(self._NEW_DATA_DICTIONARY)
