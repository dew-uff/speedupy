import time
from functools import wraps
from typing import Callable, List, Dict, Optional
import sys, os, random
sys.path.append(os.path.dirname(__file__))

from execute_exp.SpeeduPySettings import SpeeduPySettings
from logger.log import debug
from util import check_python_version
from execute_exp.data_access import get_cache_entry, get_function_call_return_freqs, create_cache_entry, close_data_access, init_data_access, add_to_metadata, get_id

from execute_exp.data_access import DataAccessConstants

def initialize_speedupy(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        DataAccessConstants().init_data_access()
        f(*method_args, **method_kwargs)
        close_data_access()
    return wrapper

#TODO: CORRIGIR IMPLEMENTAÇÃO
def maybe_deterministic(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        debug("calling {0}".format(f.__name__))

        # if revalidation.execucao_de_revalidacao():
        #     Executa função + Coleta metadados!
        #     revalidation.calcular_proxima_revalidacao()
        #     atualizar_dados_BD_com_metadados()
        # else:
        #     if (num_exec_BD < num_exec_min) and \
        #        (num_exec_BD + num_exec_metadados >= num_exec_min):
        #         atualizar_dados_BD_com_metadados()
        #     if num_exec_BD >= num_exec_min:
        #         if exec_mode.pode_acelerar_funcao():
        #             Acelera! (exec_mode.get_func_call_cache)
        #             revalidation.decrementar_cont_prox_revalidacao()
        #         else:
        #             Executa função!
        #     else:
        #         Executa função + Coleta Metadados!


        c = _get_cache_entry(f, method_args)
        returns_2_freq = _get_function_call_return_freqs(f, method_args, method_kwargs)
        if _cache_exists(c):
            debug("cache hit for {0}({1})".format(f.__name__, *method_args))
            return c
        if _returns_exist(returns_2_freq):
            debug("simulating {0}({1})".format(f.__name__, *method_args))
            ret = _simulate_func_exec(returns_2_freq)
            return ret
        else:
            debug("cache miss for {0}({1})".format(f.__name__, *method_args))
            return_value, elapsed_time = _execute_func(f, *method_args, **method_kwargs)
            if _function_call_maybe_deterministic(f, method_args, method_kwargs):
                debug("{0}({1} may be deterministic!)".format(f.__name__, *method_args))
                _save_metadata(f, method_args, method_kwargs, return_value, elapsed_time)
            return return_value
    return wrapper

def _simulate_func_exec(returns_2_freq:Dict):
    sorted_num = random.random()
    sum = 0
    for value, freq in returns_2_freq.items():
        sum += freq
        if sorted_num <= sum:
            return value

#TODO: CORRIGIR IMPLEMENTAÇÃO
def _function_call_maybe_deterministic(func: Callable, func_args:List, func_kwargs:Dict) -> bool:
    func_hash = DataAccessConstants().FUNCTIONS_2_HASHES[func.__qualname__]
    func_call_hash = get_id(func_hash, func_args, func_kwargs)
    #return func_call_hash not in Constantes().DONT_CACHE_FUNCTION_CALLS
    return True

#TODO: VERIFICAR SE ESTÁ FUNCIONANDO CONFORME ESPERADO!
def deterministic(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        debug("calling {0}".format(f.__name__))
        c = _get_cache_entry(f, method_args)
        if not _cache_exists(c):
            debug("cache miss for {0}({1})".format(f.__name__, *method_args))
            return_value, _ = _execute_func(f, *method_args, **method_kwargs)
            _create_cache_entry(f, method_args, return_value)
            return return_value
        else:
            debug("cache hit for {0}({1})".format(f.__name__, *method_args))
            return c
    return wrapper

def _cache_exists(cache) -> bool:
    return cache is not None

def _returns_exist(rets_2_freq:Optional[Dict]) -> bool:
    return rets_2_freq is not None

def _execute_func(f, self, *method_args, **method_kwargs):
    start = time.perf_counter()
    result_value = f(self, *method_args, **method_kwargs) if self is not None else f(*method_args, **method_kwargs)
    end = time.perf_counter()
    elapsed_time = end - start
    debug("{0} took {1} to run".format(f.__name__, elapsed_time))
    return result_value, elapsed_time

def _get_cache_entry(func, args):
    fun_hash = DataAccessConstants().FUNCTIONS_2_HASHES[func.__qualname__]
    return get_cache_entry(func.__name__, args, fun_hash, SpeeduPySettings().g_argsp_m)

def _get_function_call_return_freqs(f, args:List, kwargs:Dict) -> Optional[Dict]:
    f_hash = DataAccessConstants().FUNCTIONS_2_HASHES[f.__qualname__]
    return get_function_call_return_freqs(f_hash, args, kwargs)

def _create_cache_entry(func, fun_args, fun_return):
    debug("adding cache entry for {0}({1})".format(func.__name__, fun_args))
    fun_hash = DataAccessConstants().FUNCTIONS_2_HASHES[func.__qualname__]
    create_cache_entry(func.__name__, fun_args, fun_return, fun_hash, SpeeduPySettings().g_argsp_m)

def _save_metadata(func, fun_args, fun_kwargs, fun_return, elapsed_time):
    debug("adding metadata for {0}({1})".format(func.__name__, fun_args))
    fun_hash = DataAccessConstants().FUNCTIONS_2_HASHES[func.__qualname__]
    add_to_metadata(fun_hash, fun_args, fun_kwargs, fun_return, elapsed_time)


check_python_version()

if SpeeduPySettings().g_argsp_exec_mode == 'no-cache':
    def initialize_speedupy(f):
        return f

    def deterministic(f):
        return f
    
    def maybe_deterministic(f):
        return f

elif SpeeduPySettings().g_argsp_exec_mode == 'manual':
    def maybe_deterministic(f):
        return f
