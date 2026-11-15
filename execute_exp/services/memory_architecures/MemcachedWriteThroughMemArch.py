from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.memory_architecures.AbstractMemcachedArch import (
    AbstractMemcachedArch,
)


class MemcachedWriteThroughMemArch(AbstractMemcachedArch):
    def create_cache_entry(
        self, func_call_hash: str, func_return, func_name=None
    ) -> None:
        cache_data = CacheData(func_call_hash, func_return, func_name)

        self._memcached.set(func_call_hash, cache_data)
        self._retrieval_strategy.save_cache_data({func_call_hash: cache_data})

    def save_new_cache_entries(self) -> None:
        # There is nothing to save, since in write-through strategy the records are saved immediately after creation
        pass

    def get_new_cache_entries_size(self) -> int:
        # There is nothing to save, since in write-through strategy the records are saved immediately after creation
        return 0
