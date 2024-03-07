import threading
from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from data_access_util import get_file_name, serialize
from storage import save_storage, get_all_data_storage
from banco import Banco
from constantes import Constantes

#TODO: TEST
class V024MemArch(AbstractMemArch):
    def __init__(self):
        self.__CACHED_DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()
        self.__DATA_DICTIONARY = {}
        self.__NEW_DATA_DICTIONARY = {}

    def get_initial_cache_entries(self):
        def _populate_cached_data_dictionary():
            db_connection = Banco(Constantes().BD_PATH)
            data = get_all_data_storage(db_connection)
            with self.__CACHED_DATA_DICTIONARY_SEMAPHORE:
                self.__DATA_DICTIONARY = data
            db_connection.fecharConexao()
        load_cached_data_dictionary_thread = threading.Thread(target=_populate_cached_data_dictionary)
        load_cached_data_dictionary_thread.start()
    
    def get_cache_entry(self, func_call_hash:str):
        with self.__CACHED_DATA_DICTIONARY_SEMAPHORE:
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