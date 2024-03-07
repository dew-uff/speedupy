from constantes import Constantes
from typing import Dict
import os
from data_access_util import get_file_name
from util import deserialize_from_file, serialize_to_file
from constantes import Constantes
import pickle
from banco import Banco

class Storage():
    def get_all_cached_data(self, use_isolated_connection=False) -> Dict: pass
    def get_cached_data_of_a_function(self, func_name:str, use_isolated_connection=False): pass
    def get_cached_data_of_a_function_call(self, func_call_hash:str, use_isolated_connection=False): pass
    def save_cache_data_of_a_function_call(self, func_call_hash:str, func_output, func_name=None, use_isolated_connection=False): pass

#TODO: TEST
#TODO: TENTAR UTILIZAR DECORADOR PARA SETAR A CONEXÃO COM O BANCO DE DADOS!!
class DBStorage(Storage):
    # func_call_hash
    # func_output
    # func_name
    def _get_db_connection(self, use_isolated_connection:bool) -> Banco:
        db_connection = Constantes().CONEXAO_BANCO
        if use_isolated_connection: db_connection = Banco(Constantes().BD_PATH)
        return db_connection
    
    def get_all_cached_data(self, use_isolated_connection=False) -> Dict:
        db_connection = self._get_db_connection(use_isolated_connection)
        results = db_connection.executarComandoSQLSelect("SELECT func_call_hash, func_output FROM CACHE")
        data = {func_call_hash:pickle.loads(func_output) for func_call_hash, func_output in results}
        if use_isolated_connection: db_connection.fecharConexao()
        return data
    
    def get_cached_data_of_a_function(self, func_name:str, use_isolated_connection=False) -> Dict:
        db_connection = self._get_db_connection(use_isolated_connection)
        results = db_connection.executarComandoSQLSelect("SELECT func_call_hash, func_output FROM CACHE WHERE func_name = ?", (func_name,))
        data = {func_call_hash:pickle.loads(func_output) for func_call_hash, func_output in results}
        if use_isolated_connection: db_connection.fecharConexao()
        return data

    def get_cached_data_of_a_function_call(self, func_call_hash:str, use_isolated_connection=False):
        db_connection = self._get_db_connection(use_isolated_connection)
        result = db_connection.executarComandoSQLSelect("SELECT func_output FROM CACHE WHERE func_call_hash = ?", (func_call_hash,))
        func_output = pickle.loads(result[0][0])
        if use_isolated_connection: db_connection.fecharConexao()
        return func_output

    def save_cache_data_of_a_function_call(self, func_call_hash:str, func_output, func_name=None, use_isolated_connection=False):
        db_connection = self._get_db_connection(use_isolated_connection)
        func_output = pickle.dumps(func_output)
        if func_name is None:
            db_connection.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(func_call_hash, func_output) VALUES (?, ?)", (func_call_hash, func_output))
        else:
            db_connection.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(func_call_hash, func_output, func_name) VALUES (?, ?, ?)", (func_call_hash, func_output, func_name))
        if use_isolated_connection:
            db_connection.salvarAlteracoes()
            db_connection.fecharConexao()

class FileSystemStorage(Storage): pass

def get_all_cached_data_storage(conexao=Constantes().CONEXAO_BANCO) -> Dict:
    data = {}
    list_of_ipcache_files = conexao.executarComandoSQLSelect("SELECT cache_file FROM CACHE")
    for ipcache_file in list_of_ipcache_files:
        ipcache_file = ipcache_file[0].replace(".ipcache", "")
        result = deserialize(ipcache_file)
        if(result is None):
            continue
        else:
            data[ipcache_file] = result
    return data

def get_cached_data_of_a_function_storage(func_name):
    data = {}
    list_file_names = get_fun_name(func_name)
    for file_name in list_file_names:
        file_name = file_name[0].replace(".ipcache", "")
        
        result = deserialize(file_name)
        if(result is None):
            continue
        else:
            data[file_name] = result
    return data

def get_cached_data_of_a_function_call_storage(id):
    return Constantes().CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE WHERE cache_file = ?", (id,))

def save_cache_data_of_a_function_call_storage(file_name):
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(cache_file) VALUES (?)", (file_name,))

#Versão desenvolvida por causa do _save em salvarNovosDadosBanco para a v0.2.5.x e a v0.2.6.x, com o nome da função
#Testar se existe a sobrecarga
def save_cache_data_of_a_function_call_storage_with_func_name(file_name, fun_name):
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(cache_file, fun_name) VALUES (?, ?)", (file_name, fun_name))

#Versão desenvolvida por causa do _get_fun_name, que diferente do _get, recebe o nome da função ao invés do id, serve para a v0.2.5.x e a v0.2.6.x, que tem o nome da função
def get_fun_name(fun_name):
    return Constantes().CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE WHERE fun_name = ?", (fun_name,))

def deserialize(id):
    filename = os.path.join(Constantes().CACHE_FOLDER_NAME, get_file_name(id))
    return deserialize_from_file(filename)
    
def serialize(return_value, file_name):
    filename = os.path.join(Constantes().CACHE_FOLDER_NAME, get_file_name(file_name))
    serialize_to_file(return_value, filename)