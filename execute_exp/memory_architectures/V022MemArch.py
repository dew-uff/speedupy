from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from execute_exp.services.storages.Storage import Storage

#TODO: TEST
class V022MemArch(AbstractMemArch):
    def __init__(self, storage:Storage):
        #DATA_DICTIONARY armazena os dados novos ainda não persistidos no banco de dados e os dados já persitidos no banco de dados
        super().__init__(storage)
        self.__DATA_DICTIONARY = {}

    def get_initial_cache_entries(self):
        self.__DATA_DICTIONARY = self.__storage.get_all_cached_data()
    
    def get_cache_entry(self, func_call_hash:str):
        if(func_call_hash in self.__DATA_DICTIONARY):
            return self.__DATA_DICTIONARY[func_call_hash]
        return None
    
    def create_cache_entry(self, func_call_hash:str, func_return):
        self.__DATA_DICTIONARY[func_call_hash] = func_return
    
    def save_new_cache_entries(self):
        for func_call_hash, func_return in self.__DATA_DICTIONARY.items():
            self.__storage.save_cache_data_of_a_function_call(func_call_hash, func_return)