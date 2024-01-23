from typing import List, Dict, Union, Tuple, Optional
import ast, os, time
from services.function_inference_service import FunctionClassification
from constantes import Constantes
from data_access import get_all_saved_metadata_of_a_function_group_by_function_call_hash
from entities.Script import Script
from entities.Metadata import Metadata

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
        print(f"Antes: {len(func_calls_2_metadata[func_call])}")
        _try_execute_func(module, function.name, func_call, func_calls_2_metadata[func_call])
        if _get_num_executions_needed(func_calls_2_metadata[func_call]) == 0:
            if is_statistically_deterministic_function():
                classify_as_statistically_deterministic_function()
            elif should_be_simulated():
                classify_as_simulated_function_execution()

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

#TODO
def is_statistically_deterministic_function(): pass

#TODO
def classify_as_statistically_deterministic_function(): pass

#TODO
def should_be_simulated(): pass

#TODO
def classify_as_simulated_function_execution(): pass