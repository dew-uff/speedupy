import pickle
import hashlib
import os
import threading
import mmh3
import xxhash

from typing import Dict, List, Tuple, Optional
from banco import Banco
from logger.log import debug, warn
from constantes import Constantes
from entities.Metadata import Metadata
from entities.FunctionCallProv import FunctionCallProv

#TODO
def get_func_call_prov(func_call_hash:str) -> FunctionCallProv: pass
def get_func_call_prov_attr(a, b): pass
def set_func_call_prov_attr(a, b, c): pass

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
    data = pickle.dumps(fun_args) + pickle.dumps(fun_kwargs)
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


def get_function_call_return_freqs(fun_source:str, fun_args:Tuple, fun_kwargs:Dict) -> Optional[Dict]:
    try:
        func_call_hash = get_id(fun_source, fun_args, fun_kwargs)
        return Constantes().SIMULATED_FUNCTION_CALLS[func_call_hash]
    except KeyError:
        return None


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

def add_to_metadata(fun_hash:str, fun_args:List, fun_kwargs:Dict, fun_return, exec_time:float) -> None:
    md = Metadata(fun_hash, fun_args, fun_kwargs, fun_return, exec_time)
    Constantes().METADATA.append(md)

def add_to_dont_cache_function_calls(fun_hash:str, fun_args:List, fun_kwargs:Dict) -> None:
    fun_call_hash = get_id(fun_hash, fun_args, fun_kwargs)    
    Constantes().NEW_DONT_CACHE_FUNCTION_CALLS.append(fun_call_hash)

def add_to_simulated_function_calls(fun_hash:str, fun_args:List, fun_kwargs:Dict, returns_2_freq:Dict) -> None:
    fun_call_hash = get_id(fun_hash, fun_args, fun_kwargs)    
    Constantes().NEW_SIMULATED_FUNCTION_CALLS[fun_call_hash] = returns_2_freq

def close_data_access():
    __save_new_cache_data()
    _save_new_metadata()
    _save_new_dont_cache_function_calls()
    _save_new_simulated_function_calls()
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

def _save_new_metadata() -> None:
    debug("saving metadata")
    for md in Constantes().METADATA:
        s_args = pickle.dumps(md.args)
        s_kwargs = pickle.dumps(md.kwargs)
        s_return = pickle.dumps(md.return_value)
        sql = f"INSERT INTO METADATA(function_hash, args, kwargs, return_value, execution_time) VALUES (?, ?, ?, ?, ?)"
        sql_params = [md.function_hash, s_args, s_kwargs, s_return, md.execution_time]
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

def _save_new_dont_cache_function_calls() -> None:
    debug("saving don't cache function calls")
    if len(Constantes().NEW_DONT_CACHE_FUNCTION_CALLS) == 0: return
    sql = "INSERT INTO DONT_CACHE_FUNCTION_CALLS(function_call_hash) VALUES"
    sql_params = []
    for func_call_hash in Constantes().NEW_DONT_CACHE_FUNCTION_CALLS:
        sql += " (?),"
        sql_params.append(func_call_hash)
    sql = sql[:-1] # Removendo vírgula final
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

def _save_new_simulated_function_calls() -> None:
    debug("saving simulated function calls")
    if len(Constantes().NEW_SIMULATED_FUNCTION_CALLS) == 0: return
    sql = "INSERT INTO SIMULATED_FUNCTION_CALLS(function_call_hash, returns_2_freq) VALUES"
    sql_params = []
    for func_call_hash, rets_2_freq in Constantes().NEW_SIMULATED_FUNCTION_CALLS.items():
        sql += " (?, ?),"
        sql_params += [func_call_hash, pickle.dumps(rets_2_freq)]
    sql = sql[:-1] # Removendo vírgula final
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

def get_already_classified_functions() -> Dict[str, str]:
    resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(f"SELECT function_hash, classification FROM CLASSIFIED_FUNCTIONS")
    classified_functions = {}
    for reg in resp:
        classified_functions[reg[0]] = reg[1]
    return classified_functions

def get_all_saved_metadata_of_a_function_group_by_function_call_hash(func_hash:str) -> Dict[str, List[Metadata]]:
    sql = "SELECT id, args, kwargs, return_value, execution_time\
           FROM METADATA\
           WHERE function_hash = ?"
    resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql, [func_hash])
    metadata = {}
    for record in resp:
        id = int(record[0])
        args = pickle.loads(record[1])
        kwargs = pickle.loads(record[2])
        return_value = pickle.loads(record[3])
        execution_time = float(record[4])
        md = Metadata(func_hash, args, kwargs, return_value, execution_time, id=id)
        
        func_call_hash = get_id(func_hash, args, kwargs)
        if func_call_hash not in metadata:
            metadata[func_call_hash] = []
        metadata[func_call_hash].append(md)
    return metadata

def remove_metadata(metadata:List[Metadata]) -> None:
    if len(metadata) == 0: return
    sql = "DELETE FROM METADATA WHERE id IN ("
    sql_params = []
    for md in metadata:
        sql += '?,'
        sql_params.append(md.id)
    sql = sql[:-1] + ')'
    Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

def init_data_access():
    _populate_cache_dictionaries()
    _populate_dont_cache_function_calls_list()
    _populate_simulated_function_calls_dict()
    _populate_function_calls_prov_dict()

def _populate_cache_dictionaries():
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

def _populate_dont_cache_function_calls_list():
    sql = "SELECT function_call_hash FROM DONT_CACHE_FUNCTION_CALLS"
    resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
    Constantes().DONT_CACHE_FUNCTION_CALLS = []
    for func_call_hash in resp:
        Constantes().DONT_CACHE_FUNCTION_CALLS.append(func_call_hash[0])

def _populate_simulated_function_calls_dict():
    sql = "SELECT function_call_hash, returns_2_freq FROM SIMULATED_FUNCTION_CALLS"
    resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
    Constantes().SIMULATED_FUNCTION_CALLS = {}
    for func_call_hash, returns_2_freq in resp:
        Constantes().SIMULATED_FUNCTION_CALLS[func_call_hash] = pickle.loads(returns_2_freq)

#TODO: TEST
def _populate_function_calls_prov_dict():
    sql = "SELECT function_call_hash, outputs, total_num_exec, next_revalidation, next_index_weighted_seq, mode_rel_freq, mode_output, weighted_output_seq, mean_output, confidence_lv, confidence_low_limit, confidence_up_limit, confidence_error FROM FUNCTION_CALLS_PROV"
    resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
    Constantes().FUNCTION_CALLS_PROV = {}
    for reg in resp:
        function_call_hash = reg[1]
        outputs = pickle.loads(reg[2])
        total_num_exec = int(reg[3])
        next_revalidation = int(reg[4])
        next_index_weighted_seq = int(reg[5])
        mode_rel_freq = float(reg[6])
        mode_output = pickle.loads(reg[7])
        weighted_output_seq = pickle.loads(reg[8])
        mean_output = pickle.loads(reg[9])
        confidence_lv = float(reg[10])
        confidence_low_limit = float(reg[11])
        confidence_up_limit = float(reg[12])
        confidence_error = float(reg[13])
        Constantes().FUNCTION_CALLS_PROV[function_call_hash] = FunctionCallProv(function_call_hash, 
                                                                                outputs, total_num_exec, next_revalidation, next_index_weighted_seq,mode_rel_freq, mode_output, weighted_output_seq, mean_output, confidence_lv, confidence_low_limit, confidence_up_limit, confidence_error)
