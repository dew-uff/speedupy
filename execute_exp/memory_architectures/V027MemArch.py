from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from execute_exp.services.storages.Storage import Storage

#TODO: TEST
class V027MemArch(AbstractMemArch):
    def __init__(self, storage:Storage):
        super().__init__(storage)
        self.__DATA_DICTIONARY = {}
        self.__NEW_DATA_DICTIONARY = {}

    def get_initial_cache_entries(self): pass
    
    def get_cache_entry(self, func_call_hash:str, *args):
        if(func_call_hash in self.__DATA_DICTIONARY):
            return self.__DATA_DICTIONARY[func_call_hash]
        if(func_call_hash in self.__NEW_DATA_DICTIONARY):
            return self.__NEW_DATA_DICTIONARY[func_call_hash]
        
        result = self._storage.get_cached_data_of_a_function_call(func_call_hash)
        self.__DATA_DICTIONARY[func_call_hash] = result
        return result
    
    def create_cache_entry(self, func_call_hash:str, func_return, *args):
        self.__NEW_DATA_DICTIONARY[func_call_hash] = func_return

    def save_new_cache_entries(self):
        for func_call_hash, func_return in self.__NEW_DATA_DICTIONARY.items():
            self._storage.save_cache_data_of_a_function_call(func_call_hash, func_return)