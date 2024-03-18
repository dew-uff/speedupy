from execute_exp.services.revalidations.AbstractRevalidation import AbstractRevalidation
from execute_exp.entitites.Metadata import Metadata

class FixedRevalidation(AbstractRevalidation):
    def __init__(self, fixed_num_exec_til_reval:int):
        self.__fixed_num_exec_til_reval = fixed_num_exec_til_reval
    
    def calculate_next_revalidation(self, function_call_hash:str, metadata:Metadata) -> None:
        self.set_next_revalidation(self.__fixed_num_exec_til_reval, function_call_hash, force=True)
