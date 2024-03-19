from execute_exp.services.revalidations.AbstractRevalidation import AbstractRevalidation
from execute_exp.entitites.Metadata import Metadata
from execute_exp.entitites.FunctionCallProv import FunctionCallProv

class NoRevalidation(AbstractRevalidation):
    def revalidation_in_current_execution(self, func_call_hash:str) -> bool:
        return False
    
    def decrement_num_exec_to_next_revalidation(self, func_call_hash:str) -> None: return

    def set_next_revalidation(self, num_exec_2_reval:int, func_call_hash:str, force=False) -> None: return

    def calculate_next_revalidation(self, fc_prov:FunctionCallProv, metadata:Metadata) -> None: return
