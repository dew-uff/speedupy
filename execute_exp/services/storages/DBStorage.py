import pickle
from typing import Dict

from execute_exp.services.storages.Storage import Storage
from constantes import Constantes
from banco import Banco

class DBStorage(Storage):
    def __init__(self):
        self.__db_connection = Banco(Constantes().BD_PATH)

    def _set_db_connection(func):
        def wrapper(self, *args, use_isolated_connection=False, **kwargs):
            if use_isolated_connection:
                main_conn = self.__db_connection
                self.__db_connection = Banco(Constantes().BD_PATH)
                result = func(self, *args, use_isolated_connection, **kwargs)
                
                if func.__qualname__ == 'DBStorage.save_cache_data':
                    self.__db_connection.salvarAlteracoes()
                self.__db_connection.fecharConexao()
                self.__db_connection = main_conn
            else:
                result = func(self, *args, use_isolated_connection, **kwargs)
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
        try:
            result = self.__db_connection.executarComandoSQLSelect("SELECT func_output FROM CACHE WHERE func_call_hash = ?", (func_call_hash,))
            func_output = pickle.loads(result[0][0])
            return func_output
        except IndexError: pass

    @_set_db_connection
    def save_cache_data(self, data:Dict[str, Dict], use_isolated_connection=False) -> None:
        if len(data) == 0: return
        sql_stmt = ''
        sql_params = []
        for func_call_hash, func_info in data.items():
            func_name = func_info['func_name']
            func_output = pickle.dumps(func_info['output'])
            
            sql_params.append(func_call_hash)
            sql_params.append(func_output)
            if func_name: sql_params.append(func_name)
        if list(data.values())[0]['func_name']: #Testing if data records have func_name set or not!
            sql_stmt = "INSERT OR IGNORE INTO CACHE(func_call_hash, func_output, func_name) VALUES" +\
                       len(data) * " (?, ?, ?),"
        else:
            sql_stmt = "INSERT OR IGNORE INTO CACHE(func_call_hash, func_output) VALUES" +\
                       len(data) * " (?, ?),"
        sql_stmt = sql_stmt[:-1]
        self.__db_connection.executarComandoSQLSemRetorno(sql_stmt, sql_params)

    def __del__(self):
        self.__db_connection.salvarAlteracoes()
        self.__db_connection.fecharConexao()