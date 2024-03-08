from entities.Metadata import Metadata
from services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from execute_exp.data_access import get_function_call_prov_entry
from pickle import loads, dumps

class AccurateMode(AbstractExecutionMode):
    def func_call_can_be_cached(self, func_call_hash:str) -> bool:
        func_call_prov = get_function_call_prov_entry(func_call_hash)
        return len(func_call_prov.outputs) == 1
    
    def get_func_call_cache(self, func_call_hash:str):
        func_call_prov = get_function_call_prov_entry(func_call_hash)
        return loads(list(func_call_prov.outputs.keys())[0])

    def func_call_acted_as_expected(self, func_call_hash:str, metadata:Metadata):
        func_call_prov = get_function_call_prov_entry(func_call_hash)
        return len(func_call_prov.outputs) == 1 and \
               dumps(metadata.return_value) in func_call_prov.outputs
