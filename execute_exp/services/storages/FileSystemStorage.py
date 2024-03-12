import os
from typing import Dict
from util import deserialize_from_file, serialize_to_file

from execute_exp.services.storages.Storage import Storage
from constantes import Constantes

class FileSystemStorage(Storage):
    def __init__(self):
        self.__CACHE_FOLDER_NAME = Constantes().CACHE_FOLDER_NAME

    def get_all_cached_data(self) -> Dict:
        data = {}
        for file in os.listdir(self.__CACHE_FOLDER_NAME):
            file_path = os.path.join(self.__CACHE_FOLDER_NAME, file)
            data[file] = deserialize_from_file(file_path)
        return data
    
    def get_cached_data_of_a_function(self, func_name:str) -> Dict:
        try:
            data = {}
            folder_path = os.path.join(self.__CACHE_FOLDER_NAME, func_name)
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                data[file] = deserialize_from_file(file_path)
        except FileNotFoundError: pass
        finally: return data
    
    def get_cached_data_of_a_function_call(self, func_call_hash:str, func_name=None):
        try:
            folder_path = self.__CACHE_FOLDER_NAME
            if func_name:
                folder_path = os.path.join(folder_path, func_name)
            file_path = os.path.join(folder_path, func_call_hash)
            return deserialize_from_file(file_path)
        except FileNotFoundError: pass
    
    def save_cache_data(self, data:Dict[str, Dict]):
        for func_call_hash, func_info in data.items():
            self._save_cache_data_of_a_function_call(func_call_hash, func_info['output'],
                                                    func_name=func_info['func_name'])
        
    def _save_cache_data_of_a_function_call(self, func_call_hash:str, func_output, func_name=None):
        folder_path = self.__CACHE_FOLDER_NAME
        if func_name:
            folder_path = os.path.join(folder_path, func_name)
            os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, func_call_hash)
        serialize_to_file(func_output, file_path)
