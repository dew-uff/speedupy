import time
from functools import wraps
from typing import Callable, List, Dict, Optional
import sys, os, random
sys.path.append(os.path.dirname(__file__))

from execute_exp.SpeeduPySettings import SpeeduPySettings
from execute_exp.services.DataAccess import DataAccess, get_id
from logger.log import debug
from util import check_python_version
from execute_exp.services.factory import init_exec_mode, init_revalidation
from SingletonMeta import SingletonMeta
from execute_exp.entitites.Metadata import Metadata

class SpeeduPy(metaclass=SingletonMeta):
    def __init__(self):
        self.exec_mode = init_exec_mode()
        self.revalidation = init_revalidation(self.exec_mode)

def initialize_speedupy(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        DataAccess().init_data_access()
        f(*method_args, **method_kwargs)
        DataAccess().close_data_access()
    return wrapper

#TODO: CORRIGIR IMPLEMENTAÇÃO
def maybe_deterministic(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        func_hash = DataAccess().get_function_hash(f.__qualname__)
        func_call_hash = get_id(func_hash, method_args, method_kwargs)
        if SpeeduPy().revalidation.revalidation_in_current_execution(func_call_hash):
            return_value, elapsed_time = _execute_func(f, *method_args, **method_kwargs)
            
            md = Metadata(func_hash, method_args, method_kwargs, return_value, elapsed_time)
            DataAccess().add_to_metadata(func_call_hash, md)
            SpeeduPy().revalidation.calculate_next_revalidation(func_call_hash, md)
            DataAccess().add_metadata_collected_to_a_func_call_prov(func_call_hash)
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


        # OLD IMPLEMENTATION
        # c = DataAccess().get_cache_entry(f.__qualname__, method_args, method_kwargs)
        # returns_2_freq = _get_function_call_return_freqs(f, method_args, method_kwargs)
        # if _cache_exists(c):
        #     debug("cache hit for {0}({1})".format(f.__name__, *method_args))
        #     return c
        # if _returns_exist(returns_2_freq):
        #     debug("simulating {0}({1})".format(f.__name__, *method_args))
        #     ret = _simulate_func_exec(returns_2_freq)
        #     return ret
        # else:
        #     debug("cache miss for {0}({1})".format(f.__name__, *method_args))
        #     return_value, elapsed_time = _execute_func(f, *method_args, **method_kwargs)
        #     if _function_call_maybe_deterministic(f, method_args, method_kwargs):
        #         debug("{0}({1} may be deterministic!)".format(f.__name__, *method_args))
        #         # DataAccess().add_to_metadata(f.__qualname__, method_args, method_kwargs, return_value, elapsed_time)
        #     return return_value
    return wrapper

# OLD IMPLEMENTATION
# def _returns_exist(rets_2_freq:Optional[Dict]) -> bool:
#     return rets_2_freq is not None

# def _get_function_call_return_freqs(f, args:List, kwargs:Dict) -> Optional[Dict]:
#     f_hash = DataAccess().FUNCTIONS_2_HASHES[f.__qualname__]
#     return get_function_call_return_freqs(f_hash, args, kwargs)

#TODO: CORRIGIR IMPLEMENTAÇÃO
# def _function_call_maybe_deterministic(func: Callable, func_args:List, func_kwargs:Dict) -> bool:
#     func_hash = DataAccess().FUNCTIONS_2_HASHES[func.__qualname__]
#     func_call_hash = get_id(func_hash, func_args, func_kwargs)
#     #return func_call_hash not in Constantes().DONT_CACHE_FUNCTION_CALLS
#     return True

#TODO: TEST
def deterministic(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        debug("calling {0}".format(f.__name__))
        c = DataAccess().get_cache_entry(f.__qualname__, method_args, method_kwargs)
        if not _cache_exists(c):
            debug("cache miss for {0}({1})".format(f.__name__, *method_args))
            return_value, _ = _execute_func(f, *method_args, **method_kwargs)
            DataAccess().create_cache_entry(f.__qualname__, method_args, method_kwargs, return_value)
            return return_value
        else:
            debug("cache hit for {0}({1})".format(f.__name__, *method_args))
            return c
    return wrapper

def _cache_exists(cache) -> bool:
    return cache is not None

def _execute_func(f, self, *method_args, **method_kwargs):
    start = time.perf_counter()
    result_value = f(self, *method_args, **method_kwargs) if self is not None else f(*method_args, **method_kwargs)
    end = time.perf_counter()
    elapsed_time = end - start
    debug("{0} took {1} to run".format(f.__name__, elapsed_time))
    return result_value, elapsed_time

check_python_version()

if SpeeduPySettings().exec_mode == ['no-cache']:
    def initialize_speedupy(f):
        return f

    def deterministic(f):
        return f
    
    def maybe_deterministic(f):
        return f

elif SpeeduPySettings().exec_mode == ['manual']:
    def maybe_deterministic(f):
        return f
