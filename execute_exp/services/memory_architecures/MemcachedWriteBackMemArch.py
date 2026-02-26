import cloudpickle
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.memory_architecures.AbstractMemcachedArch import AbstractMemcachedArch

class MemcachedWriteBackMemArch(AbstractMemcachedArch):
    def __init__(self, retrieval_strategy, use_threads: bool):
        super().__init__(retrieval_strategy, use_threads)
        self._new_cache_keys = []

    def create_cache_entry(self, func_call_hash: str, func_return, func_name=None) -> None:
        cache_data = CacheData(func_call_hash, func_return, func_name)
        self._memcached.set(func_call_hash, cache_data)
        self._new_cache_keys.append(func_call_hash)

    def save_new_cache_entries(self) -> None:
        new_cache_data = {k:self._memcached.get(k) for k in self._new_cache_keys}
        self._retrieval_strategy.save_cache_data(new_cache_data)

    def get_new_cache_entries_size(self) -> int:
        new_cache_data = {k:self._memcached.get(k) for k in self._new_cache_keys}
        return len(cloudpickle.dumps(new_cache_data))
