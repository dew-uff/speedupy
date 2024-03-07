import pickle
import hashlib
import mmh3
import xxhash

from typing import Dict, List, Tuple, Optional
from execute_exp.SpeeduPySettings import SpeeduPySettings
from constantes import Constantes
from entities.Metadata import Metadata
from entities.FunctionCallProv import FunctionCallProv
from SingletonMeta import SingletonMeta
from util import get_content_json_file
from data_access_util import deserialize
from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch

class DataAccessConstants(metaclass=SingletonMeta):
    def __init__(self):
        self.FUNCTIONS_2_HASHES = get_content_json_file(Constantes().EXP_FUNCTIONS_FILENAME)
        self.mem_arch :AbstractMemArch

#TODO
def get_func_call_prov(func_call_hash:str) -> FunctionCallProv: pass
def get_func_call_prov_attr(a, b): pass
def set_func_call_prov_attr(a, b, c): pass


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


def init_data_access():
    DataAccessConstants().mem_arch.get_initial_cache_entries()
    _populate_function_calls_prov_dict()

def _populate_function_calls_prov_dict():
    sql = "SELECT function_call_hash, outputs, total_num_exec, next_revalidation, next_index_weighted_seq, mode_rel_freq, mode_output, weighted_output_seq, mean_output, confidence_lv, confidence_low_limit, confidence_up_limit, confidence_error FROM FUNCTION_CALLS_PROV"
    resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
    Constantes().FUNCTION_CALLS_PROV = {}
    for reg in resp:
        function_call_hash = reg[0]
        outputs = pickle.loads(reg[1])
        total_num_exec = int(reg[2])
        next_revalidation = int(reg[3])
        next_index_weighted_seq = int(reg[4])
        mode_rel_freq = float(reg[5])
        mode_output = pickle.loads(reg[6])
        weighted_output_seq = pickle.loads(reg[7])
        mean_output = pickle.loads(reg[8])
        confidence_lv = float(reg[9])
        confidence_low_limit = float(reg[10])
        confidence_up_limit = float(reg[11])
        confidence_error = float(reg[12])
        Constantes().FUNCTION_CALLS_PROV[function_call_hash] = FunctionCallProv(function_call_hash, 
                                                                                outputs, total_num_exec, next_revalidation, next_index_weighted_seq,mode_rel_freq, mode_output, weighted_output_seq, mean_output, confidence_lv, confidence_low_limit, confidence_up_limit, confidence_error)

def get_cache_entry(fun_name, fun_args, fun_source, argsp_v):
    func_call_hash = get_id(fun_source, fun_args)
    return DataAccessConstants().mem_arch.get_cache_entry(func_call_hash, fun_name)

def create_cache_entry(fun_name, fun_args, fun_return, fun_source, argsp_v):
    func_call_hash = get_id(fun_source, fun_args)
    DataAccessConstants().mem_arch.create_cache_entry(func_call_hash, fun_return, fun_name)

def close_data_access():
    DataAccessConstants().mem_arch.save_new_cache_entries()
    Constantes().CONEXAO_BANCO.salvarAlteracoes()
    Constantes().CONEXAO_BANCO.fecharConexao()

def get_function_call_return_freqs(fun_source:str, fun_args:Tuple, fun_kwargs:Dict) -> Optional[Dict]:
    try:
        func_call_hash = get_id(fun_source, fun_args, fun_kwargs)
        return Constantes().SIMULATED_FUNCTION_CALLS[func_call_hash]
    except KeyError:
        return None

def add_new_data_to_CACHED_DATA_DICTIONARY(list_file_names):
    for file_name in list_file_names:
        file_name = file_name[0].replace(".ipcache", "")
        
        result = deserialize(file_name)
        if(result is None):
            continue
        else:
            with Constantes().CACHED_DATA_DICTIONARY_SEMAPHORE:
                Constantes().DATA_DICTIONARY[file_name] = result

def add_to_metadata(fun_hash:str, fun_args:List, fun_kwargs:Dict, fun_return, exec_time:float) -> None:
    md = Metadata(fun_hash, fun_args, fun_kwargs, fun_return, exec_time)
    func_call_hash = get_id(fun_hash, fun_args, fun_kwargs)
    if func_call_hash not in Constantes().METADATA: Constantes().METADATA[func_call_hash] = [] 
    Constantes().METADATA[func_call_hash].append(md)

def update_all_function_calls_prov() -> None:
    for func_call_hash in Constantes().METADATA: update_function_call_prov(func_call_hash)

def update_function_call_prov(func_call_hash:str) -> None:
    for metadata in Constantes().METADATA[func_call_hash]:
        if func_call_hash in Constantes().FUNCTION_CALLS_PROV:
            fc_prov = Constantes().FUNCTION_CALLS_PROV.pop(func_call_hash)
            Constantes().NEW_FUNCTION_CALLS_PROV[func_call_hash] = fc_prov

        if func_call_hash not in Constantes().NEW_FUNCTION_CALLS_PROV:
            fc_prov = FunctionCallProv(func_call_hash, {}, 0, None, None, None, None, None, None, None, None, None, None)
            Constantes().NEW_FUNCTION_CALLS_PROV[func_call_hash] = fc_prov

        fc_prov = Constantes().NEW_FUNCTION_CALLS_PROV[func_call_hash]
        serial_return = pickle.dumps(metadata.return_value)
        if serial_return not in fc_prov.outputs:
            fc_prov.outputs[serial_return] = 0
        fc_prov.outputs[serial_return] += 1
        fc_prov.total_num_exec += 1
        fc_prov.next_revalidation = None
        fc_prov.next_index_weighted_seq = 0

        fc_prov.mode_rel_freq = None
        fc_prov.mode_output = None
        fc_prov.weighted_output_seq = None
        fc_prov.mean_output = None
        fc_prov.confidence_lv = None
        fc_prov.confidence_low_limit = None
        fc_prov.confidence_up_limit = None
        fc_prov.confidence_error = None
