from execute_exp.services.DataAccess import DataAccess
from execute_exp.entitites.Metadata import Metadata
from execute_exp.entitites.FunctionCallProv import FunctionCallProv

class AbstractRevalidation():
    # #TODO:TEST
    # def __init__(self, max_num_exec_til_revalidation):
    #     self.__max_num_exec_til_revalidation = max_num_exec_til_revalidation

    # #TODO:IMPLEMENT
    # def assert_next_revalidation_already_updated_by_user_setting(self):
    #     pass

    def revalidation_in_current_execution(self, fc_prov:FunctionCallProv) -> bool:
        return fc_prov.next_revalidation == 0
    
    def decrement_num_exec_to_next_revalidation(self, fc_prov:FunctionCallProv) -> None:
        fc_prov.next_revalidation -= 1
        DataAccess().create_or_update_function_call_prov_entry(fc_prov)

    def set_next_revalidation(self, num_exec_2_reval:int, fc_prov:FunctionCallProv, force=False) -> None:
        if not force:
            if fc_prov.next_revalidation <= num_exec_2_reval: return
        fc_prov.next_revalidation = num_exec_2_reval
        DataAccess().create_or_update_function_call_prov_entry(fc_prov)
        
    def calculate_next_revalidation(self, fc_prov:FunctionCallProv, metadata:Metadata) -> None: pass #Implemented by each subclass!