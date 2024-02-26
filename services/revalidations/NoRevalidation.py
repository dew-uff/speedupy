from services.revalidations.AbstractRevalidation import AbstractRevalidation
from entities.Metadata import Metadata

class NoRevalidation(AbstractRevalidation):
    def __init__(self, exec_mode_name):
        super().__init__(exec_mode_name)
    
    def revalidation_in_current_execution(self, func_call_hash:str) -> bool:
        return False
    
    def decrement_num_exec_to_next_revalidation(self, func_call_hash:str) -> None: return

    def set_next_revalidation(self, num_exec_2_reval:int, func_call_hash:str, force=False) -> None: return

    def calculate_next_revalidation(self, func_call_hash:str, metadata:Metadata) -> None: return
