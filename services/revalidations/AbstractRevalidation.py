from data_access import get_func_call_prov_attr, set_func_call_prov_attr
from entities.Metadata import Metadata

class AbstractRevalidation():
    def __init__(self, exec_mode_name:str):
        self.__exec_mode_name = exec_mode_name
    
    def revalidation_in_current_execution(self, func_call_hash:str) -> bool:
        return get_func_call_prov_attr(func_call_hash, f'num_exec_til_reval_{self.__exec_mode_name}')
    
    def decrement_num_exec_to_next_revalidation(self, func_call_hash:str) -> None:
        value = get_func_call_prov_attr(func_call_hash, f'num_exec_til_reval_{self.__exec_mode_name}')
        set_func_call_prov_attr(func_call_hash, f'num_exec_til_reval_{self.__exec_mode_name}', value - 1)

    def set_next_revalidation(self, num_exec_2_reval:int, func_call_hash:str, force=False) -> None:
        next_reval = num_exec_2_reval
        if not force:
            current_value = get_func_call_prov_attr(func_call_hash, f'num_exec_til_reval_{self.__exec_mode_name}')
            if current_value <= num_exec_2_reval: next_reval = current_value
        set_func_call_prov_attr(func_call_hash, f'num_exec_til_reval_{self.__exec_mode_name}', next_reval)
        
    def calculate_next_revalidation(self, function_call_hash:str, metadata:Metadata) -> None: pass #Implemented by each subclass!