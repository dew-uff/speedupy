from execute_exp.services.memory_architecures.AbstractTwoDictMemArch import AbstractTwoDictMemArch

class OneDictAllDataOneDictNewDataMemArch(AbstractTwoDictMemArch):       
    def create_cache_entry(self, func_call_hash:str, func_return, func_name=None):
        super().create_cache_entry(func_call_hash, func_return, func_name=func_name)
        with self._DATA_DICTIONARY_SEMAPHORE:
            self._DATA_DICTIONARY[func_call_hash] = self._NEW_DATA_DICTIONARY[func_call_hash]

