from services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from data_access import get_func_call_prov
from pickle import loads

class AccurateMode(AbstractExecutionMode):
    def func_call_can_be_cached(self, func_call_hash:str) -> bool:
        func_call_prov = get_func_call_prov(func_call_hash)
        return len(func_call_prov.outputs) == 1
    
    def get_func_call_cache(self, func_call_hash:str):
        func_call_prov = get_func_call_prov(func_call_hash)
        return loads(list(func_call_prov.outputs.keys())[0])
