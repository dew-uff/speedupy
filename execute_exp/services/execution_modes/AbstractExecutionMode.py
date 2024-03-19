from execute_exp.entitites.Metadata import Metadata

class AbstractExecutionMode():
    def __init__(self, min_num_exec:int):
        self._min_num_exec = min_num_exec

    def func_call_can_be_cached(self, func_call_hash:str) -> bool: pass #Implemented by each subclass!
    def get_func_call_cache(self, func_call_hash:str): pass #Implemented by each subclass!
    def func_call_acted_as_expected(self, func_call_hash:str, metadata:Metadata): pass #Implemented by each subclass except ProbabilisticFrequencyMode!

    @property
    def min_num_exec(self):
        return self._min_num_exec