from execute_exp.data_access import get_function_call_prov_entry, create_or_update_function_call_prov_entry
from entities.Metadata import Metadata

#TODO: TEST
class AbstractRevalidation():
    def revalidation_in_current_execution(self, func_call_hash:str) -> bool:
        fc_prov = get_function_call_prov_entry(func_call_hash)
        return fc_prov.next_revalidation == 0
    
    def decrement_num_exec_to_next_revalidation(self, func_call_hash:str) -> None:
        fc_prov = get_function_call_prov_entry(func_call_hash)
        fc_prov.next_revalidation -= 1
        create_or_update_function_call_prov_entry(func_call_hash, fc_prov)
        
    def set_next_revalidation(self, num_exec_2_reval:int, func_call_hash:str, force=False) -> None:
        fc_prov = get_function_call_prov_entry(func_call_hash)
        if not force:
            if fc_prov.next_revalidation <= num_exec_2_reval: return
        fc_prov.next_revalidation = num_exec_2_reval
        create_or_update_function_call_prov_entry(func_call_hash, fc_prov)
        
    def calculate_next_revalidation(self, function_call_hash:str, metadata:Metadata) -> None: pass #Implemented by each subclass!