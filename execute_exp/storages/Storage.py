from typing import Dict

class Storage():
    def get_all_cached_data(self, use_isolated_connection=False) -> Dict: pass
    def get_cached_data_of_a_function(self, func_name:str, use_isolated_connection=False): pass
    def get_cached_data_of_a_function_call(self, func_call_hash:str, use_isolated_connection=False): pass
    def save_cache_data_of_a_function_call(self, func_call_hash:str, func_output, func_name=None, use_isolated_connection=False): pass
