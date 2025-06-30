from typing import Dict, Optional
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy


class LazyRetrieval(AbstractRetrievalStrategy):
    def get_cache_entry(self, func_call_hash: str, func_name=None) -> Optional[CacheData]:
        return self._storage.get_cached_data_of_a_function_call(func_call_hash, func_name=None)

    def save_cache_data(self, data: Dict[str, CacheData], use_isolated_connection=False) -> None:
        for cache_data in data.values(): cache_data.func_name = None
        super().save_cache_data(data, use_isolated_connection=use_isolated_connection)
