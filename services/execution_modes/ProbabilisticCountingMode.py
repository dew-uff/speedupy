from entities.Metadata import Metadata
from services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from services.execution_modes.util import func_call_mode_output_occurs_enough
from execute_exp.data_access import get_function_call_prov_entry
from constantes import Constantes
from pickle import dumps

class ProbabilisticCountingMode(AbstractExecutionMode):
    def func_call_can_be_cached(self, func_call_hash:str) -> bool:
        return func_call_mode_output_occurs_enough(func_call_hash,
                                                   Constantes().g_argsp_min_mode_occurrence)

    def get_func_call_cache(self, func_call_hash:str):
        self.__func_call_prov = get_function_call_prov_entry(func_call_hash)
        return self.__func_call_prov.mode_output

    #TODO: TEST
    def func_call_acted_as_expected(self, func_call_hash:str, metadata:Metadata):
        func_call_prov = get_function_call_prov_entry(func_call_hash)
        return dumps(metadata.return_value) == dumps(func_call_prov.mode_output)
