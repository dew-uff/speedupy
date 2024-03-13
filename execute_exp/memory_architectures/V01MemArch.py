from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from execute_exp.services.storages.Storage import Storage

#TODO: TEST
class V01MemArch(AbstractMemArch):
    def __init__(self, storage:Storage):
        super().__init__(storage)

    def get_initial_cache_entries(self): pass
    
    def get_cache_entry(self, func_call_hash:str):
        return self._storage.get_cached_data_of_a_function_call(func_call_hash,
                                                                 use_isolated_connection=True)
    
    def create_cache_entry(self, func_call_hash:str, func_return):
        self._storage.save_cache_data_of_a_function_call(func_call_hash, func_return,
                                                          use_isolated_connection=True)
        
    def save_new_cache_entries(self): pass