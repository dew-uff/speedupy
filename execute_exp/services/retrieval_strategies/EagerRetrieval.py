from typing import Dict

from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import (
    AbstractRetrievalStrategy,
)


class EagerRetrieval(AbstractRetrievalStrategy):
    def get_initial_cache_entries(self, use_thread=False) -> Dict[str, CacheData]:
        return self._storage.get_all_cached_data(use_isolated_connection=use_thread)

    def save_cache_data(
        self, data: Dict[str, CacheData], use_isolated_connection=False
    ) -> None:
        for cache_data in data.values():
            cache_data.func_name = None
        super().save_cache_data(data, use_isolated_connection=use_isolated_connection)
