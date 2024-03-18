from execute_exp.entitites.Metadata import Metadata
from execute_exp.services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from execute_exp.services.execution_modes.util import func_call_mode_output_occurs_enough
from execute_exp.services.DataAccess import DataAccess
from pickle import dumps

class ProbabilisticCountingMode(AbstractExecutionMode):
    def __init__(self, min_mode_occurrence:int):
        self.__min_mode_occurrence = min_mode_occurrence

    def func_call_can_be_cached(self, func_call_hash:str) -> bool:
        return func_call_mode_output_occurs_enough(func_call_hash, self.__min_mode_occurrence)

    def get_func_call_cache(self, func_call_hash:str):
        self.__func_call_prov = DataAccess().get_function_call_prov_entry(func_call_hash)
        return self.__func_call_prov.mode_output

    def func_call_acted_as_expected(self, func_call_hash:str, metadata:Metadata):
        func_call_prov = DataAccess().get_function_call_prov_entry(func_call_hash)
        return dumps(metadata.return_value) == dumps(func_call_prov.mode_output)
