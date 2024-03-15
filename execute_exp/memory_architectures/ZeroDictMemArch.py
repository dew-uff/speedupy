from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from entities.CacheData import CacheData

#TODO: TEST
class ZeroDictMemArch(AbstractMemArch):
    #This MemoryArchitecture can only be used with LazyRetrieval because it saves no data on RAM!
    #Thus, it always runs sequentially!
    def get_cache_entry(self, func_call_hash:str, func_name=None):
        try: return self._retrieval_strategy.get_cache_entry(func_call_hash).output
        except AttributeError: return
    
    def create_cache_entry(self, func_call_hash:str, func_return, func_name=None):
        data = CacheData(func_call_hash, func_return, func_name)
        self._storage.save_cache_data({func_call_hash: data})
