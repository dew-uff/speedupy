from typing import Optional
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.memory_architecures.AbstractTwoDictMemArch import AbstractTwoDictMemArch


class OneDictOldDataOneDictNewDataMemArch(AbstractTwoDictMemArch):
    def _get_cache_entry_from_dict(self, func_call_hash: str) -> Optional[CacheData]:
        c = self._DATA_DICTIONARY.get(func_call_hash)
        if c: return c

        return self._NEW_DATA_DICTIONARY.get(func_call_hash)
