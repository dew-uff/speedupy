from services.revalidations.AbstractRevalidation import AbstractRevalidation
from execution_modes.AbstractExecutionMode import AbstractExecutionMode
from entities.Metadata import Metadata

class FixedRevalidation(AbstractRevalidation):
    def __init__(self, exec_mode:AbstractExecutionMode, fixed_num_exec_til_reval:int):
        super().__init__(exec_mode.name)
        self.__fixed_num_exec_til_reval = fixed_num_exec_til_reval
    
    def calculate_next_revalidation(self, function_call_hash:str, metadata:Metadata) -> None:
        self.set_next_revalidation(self.__fixed_num_exec_til_reval, function_call_hash, force=True)
