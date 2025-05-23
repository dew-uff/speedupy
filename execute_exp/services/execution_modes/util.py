from typing import List, Dict
from pickle import loads
from execute_exp.entitites.FunctionCallProv import FunctionCallProv
from execute_exp.services.DataAccess import DataAccess

def func_call_mode_output_occurs_enough(fc_prov:FunctionCallProv, min_freq:float):
    if fc_prov.mode_rel_freq is None:
        _set_statistical_mode_helpers(fc_prov)
    return fc_prov.mode_rel_freq >= min_freq

def _set_statistical_mode_helpers(fc_prov:FunctionCallProv) -> None:
    for output, freq in fc_prov.outputs.items():
        if fc_prov.mode_rel_freq is None or \
           fc_prov.mode_rel_freq < freq:
            fc_prov.mode_rel_freq = freq
            fc_prov.mode_output = output
    fc_prov.mode_rel_freq /= fc_prov.total_num_exec
    fc_prov.mode_output = loads(fc_prov.mode_output)

def function_outputs_dict_2_array(func_outputs:Dict) -> List:
    data = []
    for output, freq in func_outputs.items():
        data += freq * [loads(output)]
    return data