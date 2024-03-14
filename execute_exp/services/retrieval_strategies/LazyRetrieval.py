from typing import Dict, Optional
from entities.CacheData import CacheData
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy

class LazyRetrieval(AbstractRetrievalStrategy):
    def get_cache_entry(self, func_call_hash:str) -> Optional[CacheData]:
        return self._storage.get_cached_data_of_a_function_call(func_call_hash)