from typing import List, Dict
from pickle import loads
from entities.FunctionCallProv import FunctionCallProv
from execute_exp.services.DataAccess import DataAccess

def func_call_mode_output_occurs_enough(func_call_hash, min_freq):
    func_call_prov = DataAccess().get_function_call_prov_entry(func_call_hash)
    if func_call_prov.mode_rel_freq is None:
        _set_statistical_mode_helpers(func_call_prov)
    return func_call_prov.mode_rel_freq >= min_freq

def _set_statistical_mode_helpers(func_call_prov:FunctionCallProv) -> None:
    for output, freq in func_call_prov.outputs.items():
        if func_call_prov.mode_rel_freq is None or \
           func_call_prov.mode_rel_freq < freq:
            func_call_prov.mode_rel_freq = freq
            func_call_prov.mode_output = output
    func_call_prov.mode_rel_freq /= func_call_prov.total_num_exec
    func_call_prov.mode_output = loads(func_call_prov.mode_output)

def function_outputs_dict_2_array(func_outputs:Dict) -> List:
    data = []
    for output, freq in func_outputs.items():
        data += freq * [loads(output)]
    return data