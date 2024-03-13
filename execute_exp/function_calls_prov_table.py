import pickle
from typing import Dict, List
from constantes import Constantes
from entities.Metadata import Metadata
from entities.FunctionCallProv import FunctionCallProv
from banco import Banco

#TODO: TEST
class FunctionCallsProvTable():
    def __init__(self):
        self.__FUNCTION_CALLS_PROV = {}
        self.__NEW_FUNCTION_CALLS_PROV = {}
        self.__db_connection = Banco(Constantes().BD_PATH)

    def get_initial_function_calls_prov_entries(self) -> None:
        sql = "SELECT function_call_hash, outputs, total_num_exec, next_revalidation, next_index_weighted_seq, mode_rel_freq, mode_output, weighted_output_seq, mean_output, confidence_lv, confidence_low_limit, confidence_up_limit, confidence_error, id FROM FUNCTION_CALLS_PROV"
        resp = self.__db_connection.executarComandoSQLSelect(sql)
        for reg in resp:
            id = reg[0]
            function_call_hash = reg[1]
            outputs = pickle.loads(reg[2])

            fc_prov = FunctionCallProv(function_call_hash, outputs, id=id)
            fc_prov.total_num_exec = int(reg[3])
            fc_prov.next_revalidation = int(reg[4])
            fc_prov.next_index_weighted_seq = int(reg[5])
            fc_prov.mode_rel_freq = float(reg[6])
            fc_prov.mode_output = pickle.loads(reg[7])
            fc_prov.weighted_output_seq = pickle.loads(reg[8])
            fc_prov.mean_output = pickle.loads(reg[9])
            fc_prov.confidence_lv = float(reg[10])
            fc_prov.confidence_low_limit = float(reg[11])
            fc_prov.confidence_up_limit = float(reg[12])
            fc_prov.confidence_error = float(reg[13])

            self.__FUNCTION_CALLS_PROV[function_call_hash] = fc_prov
        
    def get_function_call_prov_entry(self, func_call_hash:str) -> FunctionCallProv:
        return self.__FUNCTION_CALLS_PROV[func_call_hash]
    
    def create_or_update_function_call_prov_entry(self, func_call_hash:str, function_call_prov:FunctionCallProv) -> None:
        self.__FUNCTION_CALLS_PROV[func_call_hash] = function_call_prov

    def add_all_metadata_collected_to_function_calls_prov(self, collected_metadata:Dict[str, List[Metadata]]) -> None:
        for func_call_hash, md_list in collected_metadata.items():
            self.add_metadata_collected_to_a_func_call_prov(func_call_hash, md_list)

    def add_metadata_collected_to_a_func_call_prov(self, func_call_hash:str, collected_metadata:List[Metadata]) -> None:
        for metadata in collected_metadata:
            if func_call_hash in self.__FUNCTION_CALLS_PROV:
                fc_prov = self.__FUNCTION_CALLS_PROV.pop(func_call_hash)
                self.__NEW_FUNCTION_CALLS_PROV[func_call_hash] = fc_prov

            if func_call_hash not in self.__NEW_FUNCTION_CALLS_PROV:
                fc_prov = FunctionCallProv(func_call_hash, {})
                self.__NEW_FUNCTION_CALLS_PROV[func_call_hash] = fc_prov

            fc_prov = self.__NEW_FUNCTION_CALLS_PROV[func_call_hash]
            serial_return = pickle.dumps(metadata.return_value)
            
            if serial_return not in fc_prov.outputs:
                fc_prov.outputs[serial_return] = 0

            fc_prov.outputs[serial_return] += 1
            fc_prov.total_num_exec += 1
            fc_prov.next_revalidation = None
            fc_prov.next_index_weighted_seq = 0

            fc_prov.mode_rel_freq = None
            fc_prov.mode_output = None
            fc_prov.weighted_output_seq = None
            fc_prov.mean_output = None
            fc_prov.confidence_lv = None
            fc_prov.confidence_low_limit = None
            fc_prov.confidence_up_limit = None
            fc_prov.confidence_error = None

    #TODO: VERIFICAR SE UM ÚNICO COMANDO SQL NÃO É MAIS EFICAZ
    #TODO: VERIFICAR SE NÃO VALE A PENA SEPARAR DADOS NOVOS DE DADOS A ATUALIZAR
    def save_function_calls_prov_entries(self):
        for fc_prov in self.__NEW_FUNCTION_CALLS_PROV:
            if fc_prov.id:
                sql = "UPDATE FUNCTION_CALLS_PROV(function_call_hash, outputs, total_num_exec, next_revalidation, next_index_weighted_seq, mode_rel_freq, mode_output, weighted_output_seq, mean_output, confidence_lv, confidence_low_limit, confidence_up_limit, confidence_error) SET function_call_hash = ?, outputs = ?, total_num_exec = ?, next_revalidation = ?, next_index_weighted_seq = ?, mode_rel_freq = ?, mode_output = ?, weighted_output_seq = ?, mean_output = ?, confidence_lv = ?, confidence_low_limit = ?, confidence_up_limit = ?, confidence_error = ?;"
            else:
                sql = "INSERT INTO FUNCTION_CALLS_PROV(function_call_hash, outputs, total_num_exec, next_revalidation, next_index_weighted_seq, mode_rel_freq, mode_output, weighted_output_seq, mean_output, confidence_lv, confidence_low_limit, confidence_up_limit, confidence_error) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

            sql_params = [fc_prov.function_call_hash, pickle.dumps(fc_prov.outputs), fc_prov.total_num_exec, fc_prov.next_revalidation, fc_prov.next_index_weighted_seq, fc_prov.mode_rel_freq, pickle.dumps(fc_prov.mode_output), pickle.dumps(fc_prov.weighted_output_seq), pickle.dumps(fc_prov.mean_output), fc_prov.confidence_lv, fc_prov.confidence_low_limit, fc_prov.confidence_up_limit, fc_prov.confidence_error]
            
            self.__db_connection.executarComandoSQLSemRetorno(sql, sql_params)

    def __del__(self):
        self.__db_connection.salvarAlteracoes()
        self.__db_connection.fecharConexao()