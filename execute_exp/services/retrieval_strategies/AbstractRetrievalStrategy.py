from typing import Dict, Optional
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.storages.Storage import Storage

#TODO: VERIFY IF IT IS WORTH RENAMING TO SAME NAME OF STORAGE METHODS!
#TODO: VERIFY IF IT IS WORTH MAKING WRAPER TO SAVE_STORAGE AND MAKE ALL MEM_ARCHS ONLY INSTANTIATE RETRIEVAL_STRATEGY AND THIS INSTANCE MANAGES THE STORAGE INSTANCE
class AbstractRetrievalStrategy():
    def __init__(self, storage:Storage):
        self._storage = storage

    def get_initial_cache_entries(self, use_thread=False) -> Dict[str, CacheData]: return {}
    def get_cache_entry(self, func_call_hash:str, func_name=None) -> Optional[CacheData]: return
    def get_function_cache_entries(self, func_name:str, use_thread=False) -> Dict[str, CacheData]: return {}