from entities.Metadata import Metadata

class AbstractExecutionMode():
    def func_call_can_be_cached(self, func_call_hash:str) -> bool: pass #Implemented by each subclass!
    def get_func_call_cache(self, func_call_hash:str): pass #Implemented by each subclass!
    def func_call_acted_as_expected(self, func_call_hash:str, metadata:Metadata): pass #Implemented by each subclass except ProbabilisticFrequencyMode!