import threading
from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from data_access_util import get_file_name, serialize
from storage import get_fun_name, save_fun_name, get_all_data_of_func_storage

#TODO: TEST
#TODO: IMPLEMENT get_cache_entry
class V026MemArch(AbstractMemArch):
    def __init__(self):
        self.__CACHED_DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()
        self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB = []
        self.__DATA_DICTIONARY = {}
        #Os valores de NEW_DATA_DICTIONARY são as tuplas (retorno_da_funcao, nome_da_funcao)
        self.__NEW_DATA_DICTIONARY = {}

    def get_initial_cache_entries(self): pass
    
    def get_cache_entry(self, func_call_hash:str, func_name:str):
        if(func_name in self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB):
            with self.__CACHED_DATA_DICTIONARY_SEMAPHORE:
                if(id in self.__DATA_DICTIONARY):
                    return self.__DATA_DICTIONARY[id]
            if(id in self.__NEW_DATA_DICTIONARY):
                return self.__NEW_DATA_DICTIONARY[id][0]
        else:
            self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(func_name)
            id_file_name = get_file_name(id)
            list_file_names = get_fun_name(func_name)
            for file_name in list_file_names:
                if(file_name[0] == id_file_name):
                    thread = threading.Thread(target=add_new_data_to_CACHED_DATA_DICTIONARY, args=(list_file_names,))
                    thread.start()

                    file_name = file_name[0].replace(".ipcache", "")
                    return deserialize(file_name)
            
            thread = threading.Thread(target=add_new_data_to_CACHED_DATA_DICTIONARY, args=(list_file_names,))
            thread.start()
        return None
    
    def create_cache_entry(self, func_call_hash:str, func_return, func_name:str):
        self.__NEW_DATA_DICTIONARY[func_call_hash] = (func_return, func_name)
    
    def save_new_cache_entries(self):
        for func_call_hash, func_return in self.__NEW_DATA_DICTIONARY.items():
            serialize(func_return[0], func_call_hash)
            save_fun_name(get_file_name(func_call_hash), func_return[1])