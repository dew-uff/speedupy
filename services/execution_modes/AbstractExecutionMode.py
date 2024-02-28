class AbstractExecutionMode():
    def func_call_can_be_cached(self, func_call_hash:str) -> bool: pass #Implemented by each subclass!
