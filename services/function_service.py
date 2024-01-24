from typing import List, Dict, Union, Tuple, Optional
import ast, os, time, pickle
from services.function_inference_service import FunctionClassification
from constantes import Constantes
from data_access import get_all_saved_metadata_of_a_function_group_by_function_call_hash
from entities.Script import Script
from entities.Metadata import Metadata
from data_access import add_to_cache, add_to_dont_cache_function_calls, remove_metadata

def decorate_function(function:ast.FunctionDef, classified_functions:Dict[str, FunctionClassification], functions2hashes:Dict[str, str]) -> None:
    if _is_already_decorated(function):
        return
    id = functions2hashes[function.qualname]
    try:
        if classified_functions[id] == FunctionClassification.CACHE.name:
            function.decorator_list.append(ast.Name("deterministic", ast.Load()))
        elif classified_functions[id] == FunctionClassification.MAYBE_CACHE.name:
            function.decorator_list.append(ast.Name("maybe_deterministic", ast.Load()))
    except KeyError:
        function.decorator_list.append(ast.Name("collect_metadata", ast.Load()))

def _is_already_decorated(function:ast.FunctionDef) -> bool:
    for decorator in function.decorator_list:
        if is_initialize_intpy_decorator(decorator) or _is_common_intpy_decorator(decorator):
            return True
    return False

def is_initialize_intpy_decorator(decorator:Union[ast.Call, ast.Name]) -> bool:
    return isinstance(decorator, ast.Call) and \
           isinstance(decorator.func, ast.Name) and \
           decorator.func.id == "initialize_intpy"

def is_execute_intpy_decorator(decorator:Union[ast.Call, ast.Name]) -> bool:
    return isinstance(decorator, ast.Name) and decorator.id  == "execute_intpy"

def _is_common_intpy_decorator(decorator:Union[ast.Call, ast.Name]) -> bool:
    return isinstance(decorator, ast.Name) and \
           decorator.id in ["deterministic", "maybe_deterministic", "collect_metadata"]

#TODO
def classify_function(module, function:ast.FunctionDef, functions_2_hashes:Dict[str, str]) -> None:
    func_hash = functions_2_hashes[function.qualname]
    func_calls_2_metadata = get_all_saved_metadata_of_a_function_group_by_function_call_hash(func_hash)

    ####DEBUG
    print("TRY EXECUTING FUNCTION!")
    print(f"function.name: {function.name}")
    print(f"function.qualname: {function.qualname}")
    print(f"len(func_calls_2_metadata): {len(func_calls_2_metadata)}")
    for a in func_calls_2_metadata:
        print(f"{a}: {len(func_calls_2_metadata[a])}")
    print("#############################")
    ####
    
    for func_call in func_calls_2_metadata:
        func_call_md = func_calls_2_metadata[func_call]
        _try_execute_func(module, function.name, func_call, func_call_md)
        if _get_num_executions_needed(func_call_md) == 0:
            stats = _get_metadata_statistics(func_call_md)
            args, kwargs = _get_args_and_kwargs_func_call(func_call_md)
            if _is_statistically_deterministic_function(stats['error_rate'],
                                                        stats['mean_exec_time']):
                classify_as_statistically_deterministic_function(function.name, args, stats['most_common_ret'], func_hash)
                #Add function to CLASSIFIED_FUNCTIONS (or exclude this table)
            elif should_be_simulated():
                classify_as_simulated_function_execution()
                #Add function to CLASSIFIED_FUNCTIONS (or exclude this table)
            else:
                add_to_dont_cache_function_calls(func_hash, args, kwargs)
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

            print(f"{function_name}({args}, {kwargs}): {ret}")

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

    stats = {'values_2_freq':values_2_freq,
             'mean_exec_time':mean_exec_time,
             'most_common_ret':most_common_ret,
             'error_rate':error_rate}
    return stats

def _is_statistically_deterministic_function(error_rate:float, mean_exec_time:float):
    return error_rate <= Constantes().MAX_ERROR_RATE and\
           mean_exec_time >= Constantes().MIN_TIME_TO_CACHE
        
def classify_as_statistically_deterministic_function(fun_name, fun_args, fun_return, fun_source) -> None:
    add_to_cache(fun_name, fun_args, fun_return, fun_source, Constantes().g_argsp_m)

#TODO
def should_be_simulated():
    #Mean execution time >= Constantes():MIN_TIME_TO_SIMULATE_FUNC_CALL
    pass

#TODO
def classify_as_simulated_function_execution():
    #Insert func_call_hash and return_values_2_frequencies on SIMULATED_FUNCTION_CALLS
    pass