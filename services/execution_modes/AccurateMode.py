from services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from data_access import get_func_call_prov

class AccurateMode(AbstractExecutionMode):
    def func_call_can_be_cached(self, func_call_hash:str) -> bool:
        self.__func_call_prov = get_func_call_prov(func_call_hash)
        return len(self.__func_call_prov.outputs) == 1
    