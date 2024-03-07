from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from data_access_util import get_file_name, serialize
from storage import save_storage, get_all_data_storage

#TODO: TEST
class V023MemArch(AbstractMemArch):
    def __init__(self):
        self.__DATA_DICTIONARY = {}
        self.__NEW_DATA_DICTIONARY = {}

    def get_initial_cache_entries(self):
        self.__DATA_DICTIONARY = get_all_data_storage()
    
    def get_cache_entry(self, func_call_hash:str):
        if(func_call_hash in self.__DATA_DICTIONARY):
            return self.__DATA_DICTIONARY[func_call_hash]
        if(func_call_hash in self.__NEW_DATA_DICTIONARY):
            return self.__NEW_DATA_DICTIONARY[func_call_hash]
        return None
    
    def create_cache_entry(self, func_call_hash:str, func_return):
        self.__NEW_DATA_DICTIONARY[func_call_hash] = func_return
    
    def save_new_cache_entries(self):
        for func_call_hash, func_return in self.__NEW_DATA_DICTIONARY.items():
            serialize(func_return, func_call_hash)
            save_storage(get_file_name(func_call_hash))