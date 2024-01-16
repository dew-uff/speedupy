import pickle
import hashlib
import os
import threading
import mmh3
import xxhash

from typing import Dict, List
from banco import Banco
from logger.log import debug, warn
from constantes import Constantes

def _save(file_name):
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(cache_file) VALUES (?)", (file_name,))


#Versão desenvolvida por causa do _save em salvarNovosDadosBanco para a v0.2.5.x e a v0.2.6.x, com o nome da função
#Testar se existe a sobrecarga
def _save_fun_name(file_name, fun_name):
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(cache_file, fun_name) VALUES (?, ?)", (file_name, fun_name))


def _get(id):
    return Constantes().CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE WHERE cache_file = ?", (id,))


#Versão desenvolvida por causa do _get_fun_name, que diferente do _get, recebe o nome da função ao invés do id, serve para a v0.2.5.x e a v0.2.6.x, que tem o nome da função
def _get_fun_name(fun_name):
    return Constantes().CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE WHERE fun_name = ?", (fun_name,))


def _remove(id):
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno("DELETE FROM CACHE WHERE cache_file = ?;", (id,))


def get_id(fun_source, fun_args=[], fun_kwargs={}):
    data = b""
    for arg in fun_args:
        data += pickle.dumps(arg)
    for arg_name, arg_value in fun_kwargs.items():
        data += pickle.dumps(arg_name) + pickle.dumps(arg_value)
    data = str(data) + fun_source
    data = data.encode('utf')
    if Constantes().g_argsp_hash[0] == 'md5':
        return hashlib.md5(data).hexdigest()
    elif Constantes().g_argsp_hash[0] == 'murmur':
        return hex(mmh3.hash128(data))[2:]
    elif Constantes().g_argsp_hash[0] == 'xxhash':
        return xxhash.xxh128_hexdigest(data)


def _get_file_name(id):
    return "{0}.{1}".format(id, "ipcache")


def _autofix(id):
    debug("starting autofix")
    debug("removing {0} from database".format(id))
    _remove(_get_file_name(id))
    debug("environment fixed")


def _deserialize(id):
    try:
        with open(os.path.join(Constantes().CACHE_FOLDER_NAME, _get_file_name(id)), 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError as e:
        warn("corrupt environment. Cache reference exists for a function in database but there is no file for it in cache folder.\
            Have you deleted cache folder?")
        _autofix(id)
        return None


def _serialize(return_value, file_name):
    with open(os.path.join(Constantes().CACHE_FOLDER_NAME, _get_file_name(file_name)), 'wb') as file:
        return pickle.dump(return_value, file, protocol=pickle.HIGHEST_PROTOCOL)


def _get_cache_data_v01x(id):
    Constantes().CONEXAO_BANCO = Banco(Constantes().BD_PATH)
    list_file_name = _get(_get_file_name(id))
    Constantes().CONEXAO_BANCO.fecharConexao()
    return _deserialize(id) if len(list_file_name) == 1 else None


def _get_cache_data_v021x(id):
    #Nesta versão, DATA_DICTIONARY armazena os dados novos ainda não
    #persistidos no banco de dados
    if(id in Constantes().DATA_DICTIONARY):
        return Constantes().DATA_DICTIONARY[id]
    list_file_name = _get(_get_file_name(id))
    return _deserialize(id) if len(list_file_name) == 1 else None


def _get_cache_data_v022x(id):
    #Nesta versão, DATA_DICTIONARY armazena os dados novos ainda não
    #persistidos no banco de dados e os dados já persitidos no banco de dados
    if(id in Constantes().DATA_DICTIONARY):
        return Constantes().DATA_DICTIONARY[id]
    return None


def _get_cache_data_v023x(id):
    if(id in Constantes().DATA_DICTIONARY):
        return Constantes().DATA_DICTIONARY[id]    
    if(id in Constantes().NEW_DATA_DICTIONARY):
        return Constantes().NEW_DATA_DICTIONARY[id]
    return None


def _get_cache_data_v024x(id):
    with Constantes().CACHED_DATA_DICTIONARY_SEMAPHORE:
        if(id in Constantes().DATA_DICTIONARY):
            return Constantes().DATA_DICTIONARY[id]
    if(id in Constantes().NEW_DATA_DICTIONARY):
        return Constantes().NEW_DATA_DICTIONARY[id]
    return None


def _get_cache_data_v025x(id, fun_name):
    if(fun_name in Constantes().FUNCTIONS_ALREADY_SELECTED_FROM_DB):
        if(id in Constantes().DATA_DICTIONARY):
            return Constantes().DATA_DICTIONARY[id]
        if(id in Constantes().NEW_DATA_DICTIONARY):
            #Nesta versão, os valores de NEW_DATA_DICTIONARY são a tupla
            #(retorno_da_funcao, nome_da_funcao)
            return Constantes().NEW_DATA_DICTIONARY[id][0]
    else:
        list_file_names = _get_fun_name(fun_name)
        for file_name in list_file_names:
            file_name = file_name[0].replace(".ipcache", "")
            
            result = _deserialize(file_name)
            if(result is None):
                continue
            else:
                Constantes().DATA_DICTIONARY[file_name] = result

        Constantes().FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(fun_name)
        if(id in Constantes().DATA_DICTIONARY):
            return Constantes().DATA_DICTIONARY[id]
    return None


def _get_cache_data_v026x(id, fun_name):
    if(fun_name in Constantes().FUNCTIONS_ALREADY_SELECTED_FROM_DB):
        with Constantes().CACHED_DATA_DICTIONARY_SEMAPHORE:
            if(id in Constantes().DATA_DICTIONARY):
                return Constantes().DATA_DICTIONARY[id]
        if(id in Constantes().NEW_DATA_DICTIONARY):
            #Nesta versão, os valores de NEW_DATA_DICTIONARY são a tupla
            #(retorno_da_funcao, nome_da_funcao)
            return Constantes().NEW_DATA_DICTIONARY[id][0]
    else:
        Constantes().FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(fun_name)        
        id_file_name = _get_file_name(id)
        list_file_names = _get_fun_name(fun_name)
        for file_name in list_file_names:
            if(file_name[0] == id_file_name):
                thread = threading.Thread(target=add_new_data_to_CACHED_DATA_DICTIONARY, args=(list_file_names,))
                thread.start()

                file_name = file_name[0].replace(".ipcache", "")
                return _deserialize(file_name)
        
        thread = threading.Thread(target=add_new_data_to_CACHED_DATA_DICTIONARY, args=(list_file_names,))
        thread.start()
    return None


#Comparável à versão v021x, mas com 2 dicionários
def _get_cache_data_v027x(id):
    if(id in Constantes().DATA_DICTIONARY):
        return Constantes().DATA_DICTIONARY[id]
    if(id in Constantes().NEW_DATA_DICTIONARY):
        return Constantes().NEW_DATA_DICTIONARY[id]
    
    list_file_name = _get(_get_file_name(id))
    result = _deserialize(id) if len(list_file_name) == 1 else None
    if(result is not None):
        Constantes().DATA_DICTIONARY[id] = result
    return result


# Aqui misturam as versões v0.2.1.x a v0.2.7.x e v01x
def get_cache_data(fun_name, fun_args, fun_source, argsp_v):
    id = get_id(fun_source, fun_args)

    if(argsp_v == ['v01x']):
        ret_get_cache_data_v01x = _get_cache_data_v01x(id)
        return ret_get_cache_data_v01x
    elif(argsp_v == ['1d-ow'] or argsp_v == ['v021x']):
        ret_get_cache_data_v021x = _get_cache_data_v021x(id)
        return ret_get_cache_data_v021x
    elif(argsp_v == ['1d-ad'] or argsp_v == ['v022x']):
        ret_get_cache_data_v022x = _get_cache_data_v022x(id)
        return ret_get_cache_data_v022x
    elif(argsp_v == ['2d-ad'] or argsp_v == ['v023x']):
        ret_get_cache_data_v023x = _get_cache_data_v023x(id)
        return ret_get_cache_data_v023x
    elif(argsp_v == ['2d-ad-t'] or argsp_v == ['v024x']):
        ret_get_cache_data_v024x = _get_cache_data_v024x(id)
        return ret_get_cache_data_v024x
    elif(argsp_v == ['2d-ad-f'] or argsp_v == ['v025x']):
        ret_get_cache_data_v025x = _get_cache_data_v025x(id, fun_name)
        return ret_get_cache_data_v025x
    elif(argsp_v == ['2d-ad-ft'] or argsp_v == ['v026x']):
        ret_get_cache_data_v026x = _get_cache_data_v026x(id, fun_name)
        return ret_get_cache_data_v026x
    elif(argsp_v == ['2d-lz'] or argsp_v == ['v027x']):
        ret_get_cache_data_v027x = _get_cache_data_v027x(id)
        return ret_get_cache_data_v027x


def add_new_data_to_CACHED_DATA_DICTIONARY(list_file_names):
    for file_name in list_file_names:
        file_name = file_name[0].replace(".ipcache", "")
        
        result = _deserialize(file_name)
        if(result is None):
            continue
        else:
            with Constantes().CACHED_DATA_DICTIONARY_SEMAPHORE:
                Constantes().DATA_DICTIONARY[file_name] = result


# Aqui misturam as versões v0.2.1.x a v0.2.7.x e v01x
def add_to_cache(fun_name, fun_args, fun_return, fun_source, argsp_v):
    id = get_id(fun_source, fun_args)
    if argsp_v == ['v01x']:
        Constantes().CONEXAO_BANCO = Banco(Constantes().BD_PATH)
        debug("serializing return value from {0}".format(id))
        _serialize(fun_return, id)
        debug("inserting reference in database")
        _save(_get_file_name(id))
        Constantes().CONEXAO_BANCO.salvarAlteracoes()
        Constantes().CONEXAO_BANCO.fecharConexao()

    elif(argsp_v == ['1d-ow'] or argsp_v == ['v021x'] or
        argsp_v == ['1d-ad'] or argsp_v == ['v022x']):
        Constantes().DATA_DICTIONARY[id] = fun_return
    elif(argsp_v == ['2d-ad'] or argsp_v == ['v023x'] or 
        argsp_v == ['2d-ad-t'] or argsp_v == ['v024x'] or
        argsp_v == ['2d-lz'] or argsp_v == ['v027x']):
        Constantes().NEW_DATA_DICTIONARY[id] = fun_return
    elif(argsp_v == ['2d-ad-f'] or argsp_v == ['v025x'] or
        argsp_v == ['2d-ad-ft'] or argsp_v == ['v026x']):
        Constantes().NEW_DATA_DICTIONARY[id] = (fun_return, fun_name)

def add_to_metadata(fun_hash, fun_args, fun_kwargs, fun_return, exec_time):
    Constantes().METADATA.append({'hash':fun_hash,
                                  'args':fun_args,
                                  'kwargs':fun_kwargs,
                                  'return':fun_return,
                                  'exec_time':exec_time})

def close_data_access():
    __save_new_cache_data()
    __save_new_metadata()
    Constantes().CONEXAO_BANCO.salvarAlteracoes()
    Constantes().CONEXAO_BANCO.fecharConexao()

# Aqui misturam as versões v0.2.1.x a v0.2.7.x
def __save_new_cache_data():
    if(Constantes().g_argsp_m == ['1d-ow'] or Constantes().g_argsp_m == ['v021x'] or
        Constantes().g_argsp_m == ['1d-ad'] or Constantes().g_argsp_m == ['v022x']):
        for id in Constantes().DATA_DICTIONARY:
            debug("serializing return value from {0}".format(id))
            _serialize(Constantes().DATA_DICTIONARY[id], id)
            debug("inserting reference in database")
            _save(_get_file_name(id))
    
    elif(Constantes().g_argsp_m == ['2d-ad'] or Constantes().g_argsp_m == ['v023x'] or
        Constantes().g_argsp_m == ['2d-ad-t'] or Constantes().g_argsp_m == ['v024x'] or
        Constantes().g_argsp_m == ['2d-lz'] or Constantes().g_argsp_m == ['v027x']):
        for id in Constantes().NEW_DATA_DICTIONARY:
            debug("serializing return value from {0}".format(id))
            _serialize(Constantes().NEW_DATA_DICTIONARY[id], id)
            debug("inserting reference in database")
            _save(_get_file_name(id))
    
    elif(Constantes().g_argsp_m == ['2d-ad-f'] or Constantes().g_argsp_m == ['v025x'] or
        Constantes().g_argsp_m == ['2d-ad-ft'] or Constantes().g_argsp_m == ['v026x']):
        for id in Constantes().NEW_DATA_DICTIONARY:
            debug("serializing return value from {0}".format(id))
            _serialize(Constantes().NEW_DATA_DICTIONARY[id][0], id)
            debug("inserting reference in database")
            _save_fun_name(_get_file_name(id), Constantes().NEW_DATA_DICTIONARY[id][1])


def __save_new_metadata() -> None:
    debug("saving metadata")
    for data in Constantes().METADATA:
        metadata_id = _add_metadata_record(data['hash'], data['return'], data['exec_time'])
        _add_function_params_records(metadata_id, data['args'], data['kwargs'])


def _add_metadata_record(fun_hash:str, fun_return, exec_time:float) -> int:
    s_return = pickle.dumps(fun_return)
    sql = f"INSERT INTO METADATA(function_hash, return_value, execution_time) VALUES (?, ?, ?)"
    sql_params = [fun_hash, s_return, exec_time]
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

    sql = "SELECT last_insert_rowid()"
    metadata_id = int(Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)[0][0])
    return metadata_id
        
def _add_function_params_records(metadata_id:int, args:List, kwargs:Dict) -> None:
    sql = "INSERT INTO FUNCTION_PARAMS(metadata_id, parameter_value, parameter_name, parameter_position) VALUES "
    sql_params = []
    i = 0
    for arg in args:
        s_arg_value = pickle.dumps(arg)
        sql += "(?, ?, ?, ?), "
        sql_params += [metadata_id, s_arg_value, None, i]
        i += 1
    for arg_name, arg_value in kwargs.items():
        s_arg_value = pickle.dumps(arg_value)
        sql += "(?, ?, ?, ?), "
        sql_params += [metadata_id, s_arg_value, arg_name, i]
        i += 1
    sql = sql[:-2] #Removendo os 2 últimos caracteres! (", ")
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

def get_already_classified_functions() -> Dict[str, str]:
    resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(f"SELECT function_hash, classification FROM CLASSIFIED_FUNCTIONS")
    classified_functions = {}
    for reg in resp:
        classified_functions[reg[0]] = reg[1]
    return classified_functions


def init_data_access():
    if(Constantes().g_argsp_m == ['1d-ad'] or Constantes().g_argsp_m == ['v022x']
        or Constantes().g_argsp_m == ['2d-ad'] or Constantes().g_argsp_m == ['v023x']):
        def _populate_cached_data_dictionary():
            list_of_ipcache_files = Constantes().CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE")
            for ipcache_file in list_of_ipcache_files:
                ipcache_file = ipcache_file[0].replace(".ipcache", "")
                result = _deserialize(ipcache_file)
                if(result is None):
                    continue
                else:
                    Constantes().DATA_DICTIONARY[ipcache_file] = result
        _populate_cached_data_dictionary()
    elif(Constantes().g_argsp_m == ['2d-ad-t'] or Constantes().g_argsp_m == ['v024x']):
        def _populate_cached_data_dictionary():
            db_connection = Banco(Constantes().BD_PATH)
            list_of_ipcache_files = db_connection.executarComandoSQLSelect("SELECT cache_file FROM CACHE")
            for ipcache_file in list_of_ipcache_files:
                ipcache_file = ipcache_file[0].replace(".ipcache", "")
                
                result = _deserialize(ipcache_file)
                if(result is None):
                    continue
                else:
                    with Constantes().CACHED_DATA_DICTIONARY_SEMAPHORE:
                        Constantes().DATA_DICTIONARY[ipcache_file] = result
            db_connection.fecharConexao()
        load_cached_data_dictionary_thread = threading.Thread(target=_populate_cached_data_dictionary)
        load_cached_data_dictionary_thread.start()
