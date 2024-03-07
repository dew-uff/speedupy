from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from data_access_util import get_file_name, serialize
from storage import get_fun_name, save_fun_name, get_all_data_of_func_storage

#TODO: TEST
class V025MemArch(AbstractMemArch):
    def __init__(self):
        self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB = []
        self.__DATA_DICTIONARY = {}
        #Os valores de NEW_DATA_DICTIONARY são as tuplas (retorno_da_funcao, nome_da_funcao)
        self.__NEW_DATA_DICTIONARY = {}

    def get_initial_cache_entries(self):  pass        
    
    def get_cache_entry(self, func_call_hash:str, func_name:str):
        if(func_name in self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB):
            if(func_call_hash in self.__DATA_DICTIONARY):
                return self.__DATA_DICTIONARY[func_call_hash]
            if(func_call_hash in self.__NEW_DATA_DICTIONARY):
                return self.__NEW_DATA_DICTIONARY[func_call_hash][0]
        else:
            self.__DATA_DICTIONARY = get_all_data_of_func_storage(func_name)
            self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(func_name)
            if(func_call_hash in self.__DATA_DICTIONARY):
                return self.__DATA_DICTIONARY[func_call_hash]
        return None
    
    def create_cache_entry(self, func_call_hash:str, func_return, func_name:str):
        self.__NEW_DATA_DICTIONARY[func_call_hash] = (func_return, func_name)
    
    def save_new_cache_entries(self):
        for func_call_hash, func_return in self.__NEW_DATA_DICTIONARY.items():
            serialize(func_return[0], func_call_hash)
            save_fun_name(get_file_name(func_call_hash), func_return[1])