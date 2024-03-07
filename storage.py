from data_access_util import deserialize
from constantes import Constantes
from typing import Dict
from banco import Banco

def get_all_data_of_func_storage(func_name):
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

def get_all_data_storage(conexao=Constantes().CONEXAO_BANCO) -> Dict:
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

def get_storage(id):
    return Constantes().CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE WHERE cache_file = ?", (id,))

def remove(id):
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno("DELETE FROM CACHE WHERE cache_file = ?;", (id,))

def save_storage(file_name):
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(cache_file) VALUES (?)", (file_name,))

#Versão desenvolvida por causa do _save em salvarNovosDadosBanco para a v0.2.5.x e a v0.2.6.x, com o nome da função
#Testar se existe a sobrecarga
def save_fun_name(file_name, fun_name):
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(cache_file, fun_name) VALUES (?, ?)", (file_name, fun_name))

#Versão desenvolvida por causa do _get_fun_name, que diferente do _get, recebe o nome da função ao invés do id, serve para a v0.2.5.x e a v0.2.6.x, que tem o nome da função
def get_fun_name(fun_name):
    return Constantes().CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE WHERE fun_name = ?", (fun_name,))
