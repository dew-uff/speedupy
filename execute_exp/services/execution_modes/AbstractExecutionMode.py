from execute_exp.entitites.Metadata import Metadata
from execute_exp.entitites.FunctionCallProv import FunctionCallProv

class AbstractExecutionMode():
    def __init__(self, min_num_exec:int):
        self._min_num_exec = min_num_exec

    def func_call_can_be_cached(self, fc_prov:FunctionCallProv) -> bool: pass #Implemented by each subclass!
    def get_func_call_cache(self, fc_prov:FunctionCallProv): pass #Implemented by each subclass!
    def func_call_acted_as_expected(self, fc_prov:FunctionCallProv, metadata:Metadata): pass #Implemented by each subclass except ProbabilisticFrequencyMode!

    @property
    def min_num_exec(self):
        return self._min_num_exec