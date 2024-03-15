from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.services.storages.Storage import Storage

#TODO: TEST
class V025MemArch(AbstractMemArch):
    def __init__(self, storage:Storage):
        #Os valores de NEW_DATA_DICTIONARY são as tuplas (retorno_da_funcao, nome_da_funcao)
        super().__init__(storage)
        self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB = []
        self.__DATA_DICTIONARY = {}
        self.__NEW_DATA_DICTIONARY = {}

    def get_initial_cache_entries(self):  pass        
    
    def get_cache_entry(self, func_call_hash:str, func_name:str):
        if(func_name in self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB):
            if(func_call_hash in self.__DATA_DICTIONARY):
                return self.__DATA_DICTIONARY[func_call_hash]
            if(func_call_hash in self.__NEW_DATA_DICTIONARY):
                return self.__NEW_DATA_DICTIONARY[func_call_hash][0]
        else:
            self.__DATA_DICTIONARY = self._storage.get_cached_data_of_a_function(func_name)
            self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(func_name)
            if(func_call_hash in self.__DATA_DICTIONARY):
                return self.__DATA_DICTIONARY[func_call_hash]
        return None
    
    def create_cache_entry(self, func_call_hash:str, func_return, func_name:str):
        self.__NEW_DATA_DICTIONARY[func_call_hash] = (func_return, func_name)
    
    def save_new_cache_entries(self):
        for func_call_hash, func_data in self.__NEW_DATA_DICTIONARY.items():
            self._storage.save_cache_data_of_a_function_call(func_call_hash, func_data[0],
                                                              func_name=func_data[1])