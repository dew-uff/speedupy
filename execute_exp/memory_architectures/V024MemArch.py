import threading
from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from execute_exp.services.storages.Storage import Storage

#TODO: TEST
class V024MemArch(AbstractMemArch):
    def __init__(self, storage:Storage):
        super().__init__(storage)
        self.__CACHED_DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()
        self.__DATA_DICTIONARY = {}
        self.__NEW_DATA_DICTIONARY = {}

    def get_initial_cache_entries(self):
        def populate_cached_data_dictionary():
            data = self._storage.get_all_cached_data(use_isolated_connection=True)
            with self.__CACHED_DATA_DICTIONARY_SEMAPHORE:
                self.__DATA_DICTIONARY = data
        t = threading.Thread(target=populate_cached_data_dictionary)
        t.start()
    
    def get_cache_entry(self, func_call_hash:str, *args):
        with self.__CACHED_DATA_DICTIONARY_SEMAPHORE:
            if(func_call_hash in self.__DATA_DICTIONARY):
                return self.__DATA_DICTIONARY[func_call_hash]
        if(func_call_hash in self.__NEW_DATA_DICTIONARY):
            return self.__NEW_DATA_DICTIONARY[func_call_hash]
        return None
    
    def create_cache_entry(self, func_call_hash:str, func_return, *args):
        self.__NEW_DATA_DICTIONARY[func_call_hash] = func_return
    
    def save_new_cache_entries(self):
        for func_call_hash, func_return in self.__NEW_DATA_DICTIONARY.items():
            self._storage.save_cache_data_of_a_function_call(func_call_hash, func_return)