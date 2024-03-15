from typing import Dict, List
import pickle
import hashlib
import mmh3
import xxhash

from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.SpeeduPySettings import SpeeduPySettings
from execute_exp.function_calls_prov_table import FunctionCallsProvTable
from entities.FunctionCallProv import FunctionCallProv
from entities.Metadata import Metadata
from SingletonMeta import SingletonMeta
from constantes import Constantes
from util import get_content_json_file
from factory import init_mem_arch

#TODO: TEST
class DataAccess(metaclass=SingletonMeta):
    def __init__(self):
        self.METADATA = {}
        self.FUNCTIONS_2_HASHES = {}
        self.mem_arch :AbstractMemArch
        self.function_calls_prov_table:FunctionCallsProvTable

    def init_data_access(self):
        self.mem_arch = init_mem_arch()
        self.function_calls_prov_table = FunctionCallsProvTable()
        self.FUNCTIONS_2_HASHES = get_content_json_file(Constantes().EXP_FUNCTIONS_FILENAME)

        self.mem_arch.get_initial_cache_entries()
        self.function_calls_prov_table.get_initial_function_calls_prov_entries()

    ############# CACHE
    def get_cache_entry(self, func_qualname, func_args, func_kwargs):
        func_hash = self.FUNCTIONS_2_HASHES[func_qualname]
        func_call_hash = get_id(func_hash, func_args, func_kwargs)
        return self.mem_arch.get_cache_entry(func_call_hash, func_qualname) #some mem_arch needs 'func_qualname', others dont use it.
    
    def create_cache_entry(self, func_qualname, func_args, func_kwargs, func_return):
        func_hash = self.FUNCTIONS_2_HASHES[func_qualname]
        func_call_hash = get_id(func_hash, func_args, func_kwargs)
        self.mem_arch.create_cache_entry(func_call_hash, func_return, func_qualname) #some mem_arch needs 'func_qualname', others dont use it.

    ############# METADATA
    def add_to_metadata(self, func_call_hash:str, metadata:Metadata) -> None:
        if func_call_hash not in self.METADATA:
            self.METADATA[func_call_hash] = [] 
        self.METADATA[func_call_hash].append(metadata)

    ############# FUNCTION_CALL_PROV
    def get_function_call_prov_entry(self, func_call_hash:str) -> FunctionCallProv:
        return self.function_calls_prov_table.get_function_call_prov_entry(func_call_hash)
    
    def create_or_update_function_call_prov_entry(self, func_call_hash:str, 
                                                  function_call_prov:FunctionCallProv) -> None:
        self.function_calls_prov_table.create_or_update_function_call_prov_entry(func_call_hash,
                                                                                 function_call_prov)

    def add_all_metadata_collected_to_function_calls_prov(self) -> None:
        self.function_calls_prov_table.add_all_metadata_collected_to_function_calls_prov(self.METADATA)
        
    def add_metadata_collected_to_a_func_call_prov(self, func_call_hash:str) -> None:
        self.function_calls_prov_table.add_metadata_collected_to_a_func_call_prov(func_call_hash,
        self.METADATA[func_call_hash])

    def close_data_access(self):
        self.mem_arch.save_new_cache_entries()
        self.function_calls_prov_table.save_function_calls_prov_entries()

def get_id(fun_source, fun_args=[], fun_kwargs={}):
    data = pickle.dumps(fun_args) + pickle.dumps(fun_kwargs)
    data = str(data) + fun_source
    data = data.encode('utf')
    if SpeeduPySettings().g_argsp_hash[0] == 'md5':
        return hashlib.md5(data).hexdigest()
    elif SpeeduPySettings().g_argsp_hash[0] == 'murmur':
        return hex(mmh3.hash128(data))[2:]
    elif SpeeduPySettings().g_argsp_hash[0] == 'xxhash':
        return xxhash.xxh128_hexdigest(data)