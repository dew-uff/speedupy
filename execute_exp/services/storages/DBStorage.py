import pickle
from typing import Dict

from execute_exp.services.storages.Storage import Storage
from constantes import Constantes
from banco import Banco

#TODO: TEST
class DBStorage(Storage):
    def __init__(self):
        self.__db_connection = Banco(Constantes().BD_PATH)

    #TODO: TESTAR SE ESTÁ FUNCIONANDO!!!
    def _set_db_connection(func):
        def wrapper(self, *args, use_isolated_connection=False, **kwargs):
            if use_isolated_connection:
                main_conn = self.__db_connection
                self.__db_connection = Banco(Constantes().BD_PATH)
                result = func(self, use_isolated_connection)
                
                if func == self.save_cache_data_of_a_function_call:
                    self.__db_connection.salvarAlteracoes()
                self.__db_connection.fecharConexao()
                self.__db_connection = main_conn
            else:
                result = func(self, use_isolated_connection)
            return result
        return wrapper

    @_set_db_connection
    def get_all_cached_data(self, use_isolated_connection=False) -> Dict:
        results = self.__db_connection.executarComandoSQLSelect("SELECT func_call_hash, func_output FROM CACHE")
        data = {func_call_hash:pickle.loads(func_output) for func_call_hash, func_output in results}
        return data
    
    @_set_db_connection
    def get_cached_data_of_a_function(self, func_name:str, use_isolated_connection=False) -> Dict:
        results = self.__db_connection.executarComandoSQLSelect("SELECT func_call_hash, func_output FROM CACHE WHERE func_name = ?", (func_name,))
        data = {func_call_hash:pickle.loads(func_output) for func_call_hash, func_output in results}
        return data

    @_set_db_connection
    def get_cached_data_of_a_function_call(self, func_call_hash:str, use_isolated_connection=False):
        result = self.__db_connection.executarComandoSQLSelect("SELECT func_output FROM CACHE WHERE func_call_hash = ?", (func_call_hash,))
        func_output = pickle.loads(result[0][0])
        return func_output

    #TODO: ATUALIZAR CONFORME NOVA ASSINATURA DO MÉTODO DA SUPERCLASSE. AGORA, RECEBE-SE TODO O CONJUNTO DE DADOS AO INVÉS DE APENAS UM DADO POR VEZ!
    #TODO: ANALISAR COMO FECHAR CONEXÃO PRINCIPAL COM O BANCO DE DADOS!
    @_set_db_connection
    def save_cache_data_of_a_function_call(self, func_call_hash:str, func_output, func_name=None, use_isolated_connection=False):
        func_output = pickle.dumps(func_output)
        if func_name is None:
            self.__db_connection.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(func_call_hash, func_output) VALUES (?, ?)", (func_call_hash, func_output))
        else:
            self.__db_connection.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(func_call_hash, func_output, func_name) VALUES (?, ?, ?)", (func_call_hash, func_output, func_name))

    def __del__(self):
        self.__db_connection.salvarAlteracoes()
        self.__db_connection.fecharConexao()