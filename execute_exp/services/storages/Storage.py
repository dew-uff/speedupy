from typing import Dict, Optional
from entities.CacheData import CacheData

class Storage():
    def get_all_cached_data(self, use_isolated_connection=False) -> Dict[str, CacheData]: pass
    def get_cached_data_of_a_function(self, func_name:str, use_isolated_connection=False) -> Dict[str, CacheData]: pass
    def get_cached_data_of_a_function_call(self, func_call_hash:str, use_isolated_connection=False) -> Optional[CacheData]: pass
    def save_cache_data(self, data:Dict[str, CacheData], use_isolated_connection=False) -> None: pass
