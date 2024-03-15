from execute_exp.services.memory_architecures.AbstractTwoDictMemArch import AbstractTwoDictMemArch

#TODO:REFACTOR
class OneDictOldDataOneDictNewData(AbstractTwoDictMemArch):
    def _get_cache_entry_from_dict(self, func_call_hash:str):
        c = super()._get_cache_entry_from_dict(func_call_hash)
        if c: return c
        if(func_call_hash in self._NEW_DATA_DICTIONARY):
            return self._NEW_DATA_DICTIONARY[func_call_hash]