from entities.FunctionCallProv import FunctionCallProv
from data_access import get_func_call_prov

def func_call_mode_output_occurs_enough(func_call_hash, min_freq):
    func_call_prov = get_func_call_prov(func_call_hash)
    if func_call_prov.mode_rel_freq is None:
        _set_statistical_mode_helpers(func_call_prov)
    return func_call_prov.mode_rel_freq >= min_freq

def _set_statistical_mode_helpers(func_call_prov:FunctionCallProv) -> None:
    for output in func_call_prov.outputs:
        if func_call_prov.mode_rel_freq is None or \
           func_call_prov.mode_rel_freq < output['freq']:
            func_call_prov.mode_rel_freq = output['freq']
            func_call_prov.mode_output = output['value']
