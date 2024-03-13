from typing import Dict

class Storage():
    def get_all_cached_data(self, use_isolated_connection=False) -> Dict: pass
    def get_cached_data_of_a_function(self, func_name:str, use_isolated_connection=False) -> Dict: pass
    def get_cached_data_of_a_function_call(self, func_call_hash:str, use_isolated_connection=False): pass
    def save_cache_data(self, data:Dict[str, Dict], use_isolated_connection=False) -> None:
        # data = {func_call_hash (str): {'func_name': (Optional[str]),
        #                                'output': (Any)}
        #        }
        pass
