from typing import Dict, Optional
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy

class LazyRetrieval(AbstractRetrievalStrategy):
    def get_cache_entry(self, func_call_hash:str, func_name=None) -> Optional[CacheData]:
        return self._storage.get_cached_data_of_a_function_call(func_call_hash, func_name)