from execute_exp.services.memory_architecures.AbstractTwoDictMemArch import AbstractTwoDictMemArch

class OneDictOldDataOneDictNewData(AbstractTwoDictMemArch):
    def _get_cache_entry_from_dict(self, func_call_hash:str):
        try:
            c = super()._get_cache_entry_from_dict(func_call_hash)
            if c: return c
            return self._NEW_DATA_DICTIONARY[func_call_hash]
        except KeyError: return