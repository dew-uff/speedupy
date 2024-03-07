from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from execute_exp.storages.Storage import Storage

#TODO: TEST
class V021MemArch(AbstractMemArch):
    def __init__(self, storage:Storage):
        #NEW_DATA_DICTIONARY armazena os dados novos ainda não persistidos no banco de dados
        super().__init__(storage)
        self.__NEW_DATA_DICTIONARY = {}

    def get_initial_cache_entries(self): pass
    
    def get_cache_entry(self, func_call_hash:str):
        if(func_call_hash in self.__NEW_DATA_DICTIONARY):
            return self.__NEW_DATA_DICTIONARY[func_call_hash]
        return self.__storage.get_cached_data_of_a_function_call(func_call_hash)
    
    def create_cache_entry(self, func_call_hash:str, func_return):
        self.__NEW_DATA_DICTIONARY[func_call_hash] = func_return
        
    def save_new_cache_entries(self):
        for func_call_hash, func_return in self.__NEW_DATA_DICTIONARY.items():
            self.__storage.save_cache_data_of_a_function_call(func_call_hash, func_return)