import os
import inspect
import time
import sys
from functools import wraps

sys.path.append(os.path.dirname(__file__))

from logger.log import debug
from constantes import Constantes
from data_access import get_cache_data, create_entry, salvarNovosDadosBanco
from services.experiment_service import create_experiment, create_experiment_function_graph

###############IMPLEMENTANDO !!!!!!!!!!!! #########################
def execute_intpy(f):
    return f

g_user_script_graph = None
g_experiment = None


def initialize_intpy(user_script_path):
    def decorator(f):
        def execution(*method_args, **method_kwargs):
            _get_experiment_function_graph(user_script_path)
            f(*method_args, **method_kwargs)
            if Constantes().g_argsp_m != ['v01x']:
                _salvarCache()
        return execution
    return decorator


def _get_experiment_function_graph(user_script_path):
    global g_experiment, g_user_script_graph
    g_experiment = create_experiment(user_script_path)
    g_user_script_graph = create_experiment_function_graph(g_experiment)


def _salvarCache():
    salvarNovosDadosBanco(Constantes().g_argsp_m)


def deterministic(f):
    return _method_call(f) if _is_method(f) else _function_call(f)


def _is_method(f):
    args = inspect.getfullargspec(f).args
    return bool(args and args[0] == 'self')


def _method_call(f):
    @wraps(f)
    def wrapper(self, *method_args, **method_kwargs):
        debug("calling {0}".format(f.__name__))
        c = _get_cache(f, method_args)
        if not _cache_exists(c):
            debug("cache miss for {0}({1})".format(f.__name__, *method_args))
            return_value, elapsed_time = _execute_func(f, self, *method_args, **method_kwargs)
            _cache_data(f, method_args, return_value, elapsed_time)
            return return_value
        else:
            debug("cache hit for {0}({1})".format(f.__name__, *method_args))
            return c
    return wrapper


def _function_call(f):
    @wraps(f)
    def wrapper(*method_args, **method_kwargs):
        debug("calling {0}".format(f.__name__))
        c = _get_cache(f, method_args)
        if not _cache_exists(c):
            debug("cache miss for {0}({1})".format(f.__name__, *method_args))
            return_value, elapsed_time = _execute_func(f, *method_args, **method_kwargs)
            _cache_data(f, method_args, return_value, elapsed_time)
            return return_value
        else:
            debug("cache hit for {0}({1})".format(f.__name__, *method_args))
            return c
    return wrapper


def _get_cache(func, args):
    fun_source = g_user_script_graph.get_source_code_executed(func)
    return get_cache_data(func.__name__, args, fun_source, Constantes().g_argsp_m)


def _cache_exists(cache):
    return cache is not None


def _execute_func(f, self, *method_args, **method_kwargs):
    start = time.perf_counter()
    result_value = f(self, *method_args, **method_kwargs) if self is not None else f(*method_args, **method_kwargs)
    end = time.perf_counter()
    elapsed_time = end - start
    debug("{0} took {1} to run".format(f.__name__, elapsed_time))
    return result_value, elapsed_time


def _cache_data(func, fun_args, fun_return, elapsed_time):
    debug("starting caching data for {0}({1})".format(func.__name__, fun_args))
    start = time.perf_counter()
    fun_source = g_user_script_graph.get_source_code_executed(func)
    create_entry(func.__name__, fun_args, fun_return, fun_source, Constantes().g_argsp_m)
    end = time.perf_counter()
    debug("caching {0} took {1}".format(func.__name__, end - start))
