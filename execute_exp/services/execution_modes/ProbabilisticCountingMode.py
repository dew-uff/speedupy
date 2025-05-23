from execute_exp.entitites.Metadata import Metadata
from execute_exp.entitites.FunctionCallProv import FunctionCallProv
from execute_exp.services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from execute_exp.services.execution_modes.util import func_call_mode_output_occurs_enough
from execute_exp.services.DataAccess import DataAccess
from pickle import dumps

class ProbabilisticCountingMode(AbstractExecutionMode):
    def __init__(self, min_num_exec, min_mode_occurrence:float):
        super().__init__(min_num_exec)
        self.__min_mode_occurrence = min_mode_occurrence

    def func_call_can_be_cached(self, fc_prov:FunctionCallProv) -> bool:
        return func_call_mode_output_occurs_enough(fc_prov, self.__min_mode_occurrence)

    def get_func_call_cache(self, fc_prov:FunctionCallProv):
        return fc_prov.mode_output

    def func_call_acted_as_expected(self, fc_prov:FunctionCallProv, metadata:Metadata):
        return dumps(metadata.return_value) == dumps(fc_prov.mode_output)
