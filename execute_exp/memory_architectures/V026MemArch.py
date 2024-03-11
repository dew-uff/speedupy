import threading
from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from execute_exp.services.storages.Storage import Storage

#TODO: TEST
class V026MemArch(AbstractMemArch):
    def __init__(self, storage:Storage):
        #Os valores de NEW_DATA_DICTIONARY são as tuplas (retorno_da_funcao, nome_da_funcao)
        super().__init__(storage)
        self.__CACHED_DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()
        self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB = []
        self.__DATA_DICTIONARY = {}
        self.__NEW_DATA_DICTIONARY = {}

    def get_initial_cache_entries(self): pass
    
    def get_cache_entry(self, func_call_hash:str, func_name:str):
        def update_DATA_DICTIONARY():
            data = self.__storage.get_cached_data_of_a_function(func_name, use_isolated_connection=True)
            with self.__CACHED_DATA_DICTIONARY_SEMAPHORE:
                self.__DATA_DICTIONARY = data

        if(func_name in self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB):
            with self.__CACHED_DATA_DICTIONARY_SEMAPHORE:
                if(id in self.__DATA_DICTIONARY):
                    return self.__DATA_DICTIONARY[id]
            if(id in self.__NEW_DATA_DICTIONARY):
                return self.__NEW_DATA_DICTIONARY[id][0]
        else:
            self.__FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(func_name)
            thread = threading.Thread(target=update_DATA_DICTIONARY)
            thread.start()
            return self.__storage.get_cached_data_of_a_function_call(func_call_hash)
        return None
    
    def create_cache_entry(self, func_call_hash:str, func_return, func_name:str):
        self.__NEW_DATA_DICTIONARY[func_call_hash] = (func_return, func_name)
    
    def save_new_cache_entries(self):
        for func_call_hash, func_data in self.__NEW_DATA_DICTIONARY.items():
            self.__storage.save_cache_data_of_a_function_call(func_call_hash, func_data[0],
                                                              func_name=func_data[1])