from typing import List, Dict, Tuple
import ast, time
from constantes import Constantes
from entities.Metadata import Metadata
from execute_exp.data_access import DataAccess

#TODO TEST
def execute_and_classify_function(module, function:ast.FunctionDef, functions_2_hashes:Dict[str, str]) -> None:
    func_hash = functions_2_hashes[function.qualname]
    func_calls_2_metadata = get_all_saved_metadata_of_a_function_group_by_function_call_hash(func_hash)
    for func_call in func_calls_2_metadata:
        func_call_md = func_calls_2_metadata[func_call]
        _try_execute_func(module, function.name, func_call, func_call_md)
        if _get_num_executions_needed(func_call_md) == 0:
            _classify_function(function, func_hash, func_call_md)
            remove_metadata(func_call_md)

def _try_execute_func(module, function_name:str, func_call_hash:str, func_call_metadata:List[Metadata]) -> None:
    try:
        args, kwargs = _get_args_and_kwargs_func_call(func_call_metadata)
        num_exec = _get_num_executions_needed(func_call_metadata)
        for i in range(num_exec):
            func = getattr(module, function_name)
            start = time.perf_counter()
            ret = func(*args, **kwargs)
            end = time.perf_counter()
            elapsed_time = end - start
            md = Metadata(func_call_hash, args, kwargs, ret, elapsed_time)
            func_call_metadata.append(md)
    except Exception:
        pass

def _get_args_and_kwargs_func_call(func_call_metadata:List[Metadata]) -> Tuple[Tuple, Dict]:
    a_metadata = func_call_metadata[0]
    return a_metadata.args, a_metadata.kwargs

def _get_num_executions_needed(func_call_metadata:List[Metadata]) -> int:
    num_exec = Constantes().NUM_EXEC_MIN_PARA_INFERENCIA - len(func_call_metadata)
    if num_exec < 0:
        return 0
    return num_exec

def _classify_function(function:ast.FunctionDef, func_hash:str, func_call_md:List[Metadata]) -> None:
    stats = _get_metadata_statistics(func_call_md)
    args, kwargs = _get_args_and_kwargs_func_call(func_call_md)
    if _is_statistically_deterministic_function(stats['error_rate'],
                                                stats['mean_exec_time']):
        classify_as_statistically_deterministic_function(function.name, args, stats['most_common_ret'], func_hash)
    elif _should_be_simulated(stats['mean_exec_time']):
        classify_as_simulated_function_execution(func_hash, args, kwargs, stats['values_2_freq'])
    else:
        add_to_dont_cache_function_calls(func_hash, args, kwargs)

def _get_metadata_statistics(func_call_metadata:List[Metadata]) -> Dict:
    values_2_freq = {}
    mean_exec_time = 0
    most_common_ret = None
    for md in func_call_metadata:
        ret = md.return_value
        if ret not in values_2_freq:
            values_2_freq[ret] = 0
        values_2_freq[ret] += 1

        if most_common_ret is None or \
           values_2_freq[ret] > values_2_freq[most_common_ret]:
            most_common_ret = ret
        
        mean_exec_time += md.execution_time
    mean_exec_time /= len(func_call_metadata)
    error_rate = 1 - values_2_freq[most_common_ret] / len(func_call_metadata)
    for value in values_2_freq:
        values_2_freq[value] /= len(func_call_metadata)

    stats = {'values_2_freq':values_2_freq,
             'mean_exec_time':mean_exec_time,
             'most_common_ret':most_common_ret,
             'error_rate':error_rate}
    return stats

def _is_statistically_deterministic_function(error_rate:float, mean_exec_time:float) -> bool:
    return error_rate <= Constantes().MAX_ERROR_RATE and\
           mean_exec_time >= Constantes().MIN_TIME_TO_CACHE
        
#TODO: CHECK IF THIS FUNCTION IS WORKIN AS EXPECTED
def classify_as_statistically_deterministic_function(fun_name, fun_args, fun_return, fun_source) -> None:
    DataAccess().create_cache_entry(fun_name, fun_args, {}, fun_return)

def _should_be_simulated(mean_exec_time:float) -> bool:
    return mean_exec_time >= Constantes().MIN_TIME_TO_SIMULATE_FUNC_CALL

def classify_as_simulated_function_execution(fun_hash:str, fun_args:List, fun_kwargs:Dict, returns_2_freq:Dict) -> None:
    add_to_simulated_function_calls(fun_hash, fun_args, fun_kwargs, returns_2_freq)
