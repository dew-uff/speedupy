from execute_exp.services.storages.Storage import Storage
from execute_exp.memory_architectures.MemArchImpl import AbstractRetrievalStrategy

class AbstractMemArch():
    def __init__(self, storage:Storage, retrieval_strategy:AbstractRetrievalStrategy, use_threads:bool):
        self._storage = storage
        self._retrieval_strategy = retrieval_strategy
        self._use_threads = use_threads

    def get_initial_cache_entries(self) -> None: return
    def get_cache_entry(self, func_call_hash:str, func_name=None): pass
    def create_cache_entry(self, func_call_hash:str, func_return, func_name=None): pass
    def save_new_cache_entries(self) -> None: return
