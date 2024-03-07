import threading
from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from data_access_util import get_file_name, serialize, deserialize
from storage import get_storage, save_storage

#TODO: TEST
class V027MemArch(AbstractMemArch):
    def __init__(self):
        self.__DATA_DICTIONARY = {}
        self.__NEW_DATA_DICTIONARY = {}

    def get_initial_cache_entries(self): pass
    
    def get_cache_entry(self, func_call_hash:str):
        if(func_call_hash in self.__DATA_DICTIONARY):
            return self.__DATA_DICTIONARY[func_call_hash]
        if(func_call_hash in self.__NEW_DATA_DICTIONARY):
            return self.__NEW_DATA_DICTIONARY[func_call_hash]
        
        list_file_name = get_storage(get_file_name(func_call_hash))
        result = deserialize(func_call_hash) if len(list_file_name) == 1 else None
        if(result is not None):
            self.__DATA_DICTIONARY[func_call_hash] = result
        return result
    
    def create_cache_entry(self, func_call_hash:str, func_return):
        self.__NEW_DATA_DICTIONARY[func_call_hash] = func_return

    def save_new_cache_entries(self):
        for func_call_hash, func_return in self.__NEW_DATA_DICTIONARY.items():
            serialize(func_return, func_call_hash)
            save_storage(get_file_name(func_call_hash))