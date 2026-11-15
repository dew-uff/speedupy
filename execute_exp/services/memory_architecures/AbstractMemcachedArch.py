import threading
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from entities.BancoMemcached import BancoMemcached


class AbstractMemcachedArch(AbstractMemArch):
    def __init__(self, retrieval_strategy, use_threads: bool):
        super().__init__(retrieval_strategy, use_threads)
        self._memcached = BancoMemcached()
        self._thread = None  # Needed for unit testing!

    def get_initial_cache_entries(self) -> None:
        def populate_memcached():
            data = self._retrieval_strategy.get_initial_cache_entries(
                use_thread=self._use_threads
            )
            self._memcached.set_group_of_key_value_pairs(data)

        if self._use_threads:
            self._thread = threading.Thread(target=populate_memcached)
            self._thread.start()
        else:
            populate_memcached()

    def get_cache_entry(self, func_call_hash: str, func_name=None):
        cached_value = self._memcached.get(func_call_hash)
        if cached_value:
            return cached_value.output

        self._get_function_entries_from_storage(func_name)
        cached_value = self._memcached.get(func_call_hash)
        if cached_value:
            return cached_value.output

        persistent_cache_data = self._retrieval_strategy.get_cache_entry(
            func_call_hash, func_name
        )
        if persistent_cache_data:
            self._memcached.set(func_call_hash, persistent_cache_data)
            return persistent_cache_data.output

        return None

    def _get_function_entries_from_storage(self, func_name: str) -> None:
        def update_memcached():
            data = self._retrieval_strategy.get_function_cache_entries(
                func_name, use_thread=self._use_threads
            )
            self._memcached.set_group_of_key_value_pairs(data)

        if self._use_threads:
            self._thread = threading.Thread(target=update_memcached)
            self._thread.start()
        else:
            update_memcached()

    def create_cache_entry(
        self, func_call_hash: str, func_return, func_name=None
    ) -> None:
        pass  # Implemented by each subclass!

    def save_new_cache_entries(self) -> None:
        pass  # Implemented by each subclass!

    def get_new_cache_entries_size(self) -> int:
        pass  # Implemented by each subclass!
