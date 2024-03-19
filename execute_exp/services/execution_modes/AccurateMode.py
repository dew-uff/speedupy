from execute_exp.entitites.Metadata import Metadata
from execute_exp.entitites.FunctionCallProv import FunctionCallProv
from execute_exp.services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from execute_exp.services.DataAccess import DataAccess
from pickle import loads, dumps

class AccurateMode(AbstractExecutionMode):
    def func_call_can_be_cached(self, func_call_hash:str) -> bool:
        func_call_prov = DataAccess().get_function_call_prov_entry(func_call_hash)
        return len(func_call_prov.outputs) == 1
    
    def get_func_call_cache(self, func_call_hash:str):
        func_call_prov = DataAccess().get_function_call_prov_entry(func_call_hash)
        return loads(list(func_call_prov.outputs.keys())[0])

    def func_call_acted_as_expected(self, fc_prov:FunctionCallProv, metadata:Metadata):
        return len(fc_prov.outputs) == 1 and \
               dumps(metadata.return_value) in fc_prov.outputs
