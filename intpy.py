import sys, os
sys.path.append(os.path.dirname(__file__))

from constantes import Constantes

if Constantes().g_argsp_no_cache:
    def collect_metadata(f):
        return f
    
    def maybe_deterministic(f):
        return f
    
    def deterministic(f):
        return f
else:
    import inspect
    import time
    from functools import wraps

    from logger.log import debug
    from util import get_content_json_file
    from data_access import get_cache_data, add_to_cache, close_data_access, init_data_access, add_to_metadata

    def execute_intpy(f):
        @wraps(f)
        def wrapper(*method_args, **method_kwargs):
            Constantes().set_paths_for_executing_inside_temp_folder()
            init_data_access()
            _get_experiment_function_hashes()
            f(*method_args, **method_kwargs)
            if Constantes().g_argsp_m != ['v01x']:
                close_data_access()
        return wrapper

    g_functions2hashes = None

    def _get_experiment_function_hashes():
        global g_functions2hashes
        g_functions2hashes = get_content_json_file(Constantes().EXP_FUNCTIONS_FILENAME)

    
    #TODO
    def maybe_deterministic(f):
        return f


    #TODO TEST
    def collect_metadata(f):
        @wraps(f)
        def wrapper(*method_args, **method_kwargs):
            return_value, elapsed_time = _execute_func(f, *method_args, **method_kwargs)
            _save_metadata(f, method_args, method_kwargs, return_value, elapsed_time)
            return return_value
        return wrapper


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
        fun_hash = g_functions2hashes[func.__qualname__]
        return get_cache_data(func.__name__, args, fun_hash, Constantes().g_argsp_m)


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
        fun_hash = g_functions2hashes[func.__qualname__]
        add_to_cache(func.__name__, fun_args, fun_return, fun_hash, Constantes().g_argsp_m)
        end = time.perf_counter()
        debug("caching {0} took {1}".format(func.__name__, end - start))


    def _save_metadata(func, fun_args, fun_kwargs, fun_return, elapsed_time):
        debug("saving metadata for {0}({1})".format(func.__name__, fun_args))
        fun_hash = g_functions2hashes[func.__qualname__]
        add_to_metadata(fun_hash, fun_args, fun_kwargs, fun_return, elapsed_time)
