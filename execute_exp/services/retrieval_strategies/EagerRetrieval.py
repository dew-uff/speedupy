from typing import Dict, Optional
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy
from execute_exp.services.storages.Storage import Storage


class EagerRetrieval(AbstractRetrievalStrategy):
    def __init__(self, storage: Storage):
        super().__init__(storage)
        # None until the initial loading returns. With the thread execution mode,
        # it stays None while the loading thread is still running.
        self._loaded_entries = None

    def get_initial_cache_entries(self, use_thread=False) -> Dict[str, CacheData]:
        data = self._storage.get_all_cached_data(use_isolated_connection=use_thread)
        self._loaded_entries = data
        return data

    def get_cache_entry(self, func_call_hash: str, func_name=None) -> Optional[CacheData]:
        # The memory architecture calls this method when a call is not in RAM.
        if self._loaded_entries is None:
            # The initial loading has not finished: the result may be persisted
            # but not loaded yet, so it is looked up in the storage instead of
            # being recomputed. Eager saves the entries without func_name.
            return self._storage.get_cached_data_of_a_function_call(func_call_hash, func_name=None)
        # The initial loading has finished: the storage is not accessed again.
        # The loaded entries are checked because the memory architecture may not
        # have stored them in RAM yet when the loading has just finished.
        return self._loaded_entries.get(func_call_hash)

    def save_cache_data(self, data: Dict[str, CacheData], use_isolated_connection=False) -> None:
        for cache_data in data.values(): cache_data.func_name = None
        super().save_cache_data(data, use_isolated_connection=use_isolated_connection)
