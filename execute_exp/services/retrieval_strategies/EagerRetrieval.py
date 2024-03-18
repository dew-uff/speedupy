from typing import Dict
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy

class EagerRetrieval(AbstractRetrievalStrategy):
    def get_initial_cache_entries(self, use_thread=False) -> Dict[str, CacheData]:
        return self._storage.get_all_cached_data(use_isolated_connection=use_thread)
