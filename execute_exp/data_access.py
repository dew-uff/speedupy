from typing import Dict, List
import pickle
import hashlib
import mmh3
import xxhash

from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from execute_exp.SpeeduPySettings import SpeeduPySettings
from execute_exp.function_calls_prov_table import FunctionCallsProvTable
from entities.FunctionCallProv import FunctionCallProv
from entities.Metadata import Metadata
from SingletonMeta import SingletonMeta
from constantes import Constantes
from util import get_content_json_file

#TODO: migrar funções para essa classe DataAccessConstants e renomeá-la para DataAccess
#TODO: fazer com que essa classe armazene Constantes().CONEXAO_BANCO
class DataAccessConstants(metaclass=SingletonMeta):
    def __init__(self):
        self.METADATA = {}
        self.FUNCTIONS_2_HASHES = get_content_json_file(Constantes().EXP_FUNCTIONS_FILENAME)
        self.mem_arch :AbstractMemArch
        self.function_calls_prov_table = FunctionCallsProvTable()

    def init_data_access(self):
        self.mem_arch.get_initial_cache_entries()
        self.function_calls_prov_table.get_initial_function_calls_prov_entries()

############# CACHE
def get_cache_entry(fun_name, fun_args, fun_source, argsp_v):
    func_call_hash = get_id(fun_source, fun_args)
    return DataAccessConstants().mem_arch.get_cache_entry(func_call_hash, fun_name)

def create_cache_entry(fun_name, fun_args, fun_return, fun_source, argsp_v):
    func_call_hash = get_id(fun_source, fun_args)
    DataAccessConstants().mem_arch.create_cache_entry(func_call_hash, fun_return, fun_name)


############# METADATA
def add_to_metadata(fun_hash:str, fun_args:List, fun_kwargs:Dict, fun_return, exec_time:float) -> None:
    md = Metadata(fun_hash, fun_args, fun_kwargs, fun_return, exec_time)
    func_call_hash = get_id(fun_hash, fun_args, fun_kwargs)
    if func_call_hash not in DataAccessConstants().METADATA:
        DataAccessConstants().METADATA[func_call_hash] = [] 
    DataAccessConstants().METADATA[func_call_hash].append(md)


############# FUNCTION_CALL_PROV
def get_function_call_prov_entry(func_call_hash:str) -> FunctionCallProv:
    return DataAccessConstants().function_calls_prov_table.get_function_call_prov_entry(func_call_hash)
    
def create_or_update_function_call_prov_entry(func_call_hash:str, function_call_prov:FunctionCallProv) -> None:
    DataAccessConstants().function_calls_prov_table.create_or_update_function_call_prov_entry(func_call_hash,
                                                                                              function_call_prov)

def add_all_metadata_collected_to_function_calls_prov() -> None:
    DataAccessConstants().function_calls_prov_table.add_all_metadata_collected_to_function_calls_prov(DataAccessConstants().METADATA)
    
def add_metadata_collected_to_a_func_call_prov(func_call_hash:str) -> None:
    DataAccessConstants().function_calls_prov_table.add_metadata_collected_to_a_func_call_prov(func_call_hash,
                                                                                               DataAccessConstants().METADATA[func_call_hash])

                
def close_data_access():
    DataAccessConstants().mem_arch.save_new_cache_entries()
    DataAccessConstants().function_calls_prov_table.save_function_calls_prov_entries()
    Constantes().CONEXAO_BANCO.salvarAlteracoes()
    Constantes().CONEXAO_BANCO.fecharConexao()


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