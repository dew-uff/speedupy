import time, sys, os
from functools import wraps
from typing import Dict, List, Tuple, Any
sys.path.append(os.path.dirname(__file__))

from execute_exp.entitites.FunctionCallProv import FunctionCallProv
from execute_exp.services.factory import init_exec_mode, init_revalidation
from execute_exp.services.DataAccess import DataAccess, get_id
from execute_exp.SpeeduPySettings import SpeeduPySettings
from execute_exp.entitites.Metadata import Metadata
from SingletonMeta import SingletonMeta
from util import check_python_version
from logger.log import debug

def initialize_speedupy(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        DataAccess().init_data_access()
        f(*method_args, **method_kwargs)
        DataAccess().close_data_access()
    return wrapper

def deterministic(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        debug("calling {0}".format(f.__qualname__))
        c = DataAccess().get_cache_entry(f.__qualname__, method_args, method_kwargs)
        if _cache_doesnt_exist(c):
            debug("cache miss for {0}({1})".format(f.__qualname__, method_args))
            return_value = f(*method_args, **method_kwargs)
            DataAccess().create_cache_entry(f.__qualname__, method_args, method_kwargs, return_value)
            return return_value
        else:
            debug("cache hit for {0}({1})".format(f.__qualname__, method_args))
            return c
    return wrapper

def _cache_doesnt_exist(cache) -> bool:
    return cache is None

class SpeeduPy(metaclass=SingletonMeta):
    def __init__(self):
        self.exec_mode = init_exec_mode()
        self.revalidation = init_revalidation(self.exec_mode)

#TODO: TEST
def maybe_deterministic(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        f_hash = DataAccess().get_function_hash(f.__qualname__)
        fc_hash = get_id(f_hash, method_args, method_kwargs)
        fc_prov = DataAccess().get_function_call_prov_entry(fc_hash)
        if SpeeduPy().revalidation.revalidation_in_current_execution(fc_prov):
            result = _revalidate_func(f, method_args, method_kwargs, f_hash, fc_hash, fc_prov)
        else:
            if _updating_FunctionCallProv_may_speed_up_func_call(fc_hash, fc_prov):
                DataAccess().add_metadata_collected_to_a_func_call_prov(fc_prov)

            if _FunctionCallProv_has_enough_data_to_classify_func_call(fc_prov):
                if SpeeduPy().exec_mode.func_call_can_be_cached(fc_prov):
                    SpeeduPy().revalidation.decrement_num_exec_to_next_revalidation(fc_prov)
                    result = SpeeduPy().exec_mode.get_func_call_cache(fc_prov)
                else:
                    result = f(*method_args, **method_kwargs)
            else:
                result, _ = _execute_func_collecting_metadata(f, method_args, method_kwargs, f_hash, fc_hash)
        return result
    return wrapper

def _revalidate_func(f, method_args:List, method_kwargs:Dict, f_hash:str, fc_hash:str, fc_prov:FunctionCallProv) -> Any:
    result, md = _execute_func_collecting_metadata(f, method_args, method_kwargs, f_hash, fc_hash)
    SpeeduPy().revalidation.calculate_next_revalidation(fc_prov, md)
    DataAccess().add_metadata_collected_to_a_func_call_prov(fc_prov)
    return result

def _execute_func_collecting_metadata(f, method_args:List, method_kwargs:Dict,
                                      func_hash:str, func_call_hash:str) -> Tuple[Any, Metadata]:
    return_value, elapsed_time = _execute_func_measuring_time(f, *method_args, **method_kwargs)
    md = Metadata(func_hash, method_args, method_kwargs, return_value, elapsed_time)
    DataAccess().add_to_metadata(func_call_hash, md)
    return return_value, md

def _execute_func_measuring_time(f, method_args, method_kwargs):
    start = time.perf_counter()
    result_value = f(*method_args, **method_kwargs)
    end = time.perf_counter()
    return result_value, end - start

def _updating_FunctionCallProv_may_speed_up_func_call(fc_hash:str, fc_prov:FunctionCallProv) -> bool:
    num_metadata = DataAccess().get_amount_of_collected_metadata(fc_hash)
    return (fc_prov.total_num_exec < SpeeduPy().exec_mode.min_num_exec) and \
           (fc_prov.total_num_exec + num_metadata >= SpeeduPy().exec_mode.min_num_exec)

def _FunctionCallProv_has_enough_data_to_classify_func_call(fc_prov:FunctionCallProv) -> bool:
    return fc_prov.total_num_exec >= SpeeduPy().exec_mode.min_num_exec

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
