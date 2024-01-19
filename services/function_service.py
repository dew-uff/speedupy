from typing import List, Dict, Union, Tuple, Optional
import ast, pickle
from typing import Dict, Union
from services.function_inference_service import FunctionClassification
from constantes import Constantes
from data_access import get_all_saved_metadata_of_a_function_group_by_function_call_hash

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
        if _is_initialize_intpy_decorator(decorator) or _is_common_intpy_decorator(decorator):
            return True
    return False

def _is_initialize_intpy_decorator(decorator:Union[ast.Call, ast.Name]) -> bool:
    return isinstance(decorator, ast.Call) and \
           isinstance(decorator.func, ast.Name) and \
           decorator.func.id == "initialize_intpy"

def _is_common_intpy_decorator(decorator:Union[ast.Call, ast.Name]) -> bool:
    return isinstance(decorator, ast.Name) and \
           decorator.id in ["deterministic", "maybe_deterministic", "collect_metadata"]

#TODO
def classify_function(function:ast.FunctionDef, functions_2_hashes:Dict[str, str]) -> None:
    func_hash = functions_2_hashes[function.qualname]
    func_calls_2_metadata = get_all_saved_metadata_of_a_function_group_by_function_call_hash(func_hash)
    
    #Defining function
    function.decorator_list = []
    code = ast.unparse(function)
    print("================")
    print("Defining function:\n")
    print(code)
    print("================\n")
    exec(code)
    for f_call in func_calls_2_metadata:
        args = func_calls_2_metadata[f_call][0].args
        kwargs = func_calls_2_metadata[f_call][0].kwargs

        print(type(args))
        args = list(args)
        print(args)
        print(type(args))

        print(kwargs)
        print(type(kwargs))

        #Executing function
        code = f'\nret = {function.name}(*{args}, **{kwargs})\nprint("oi")\nprint(ret)\nprint("oi")'
        print("================")
        print("Executing function:\n")
        print(code)
        print("================\n")
        
        exec(code)
        my_ret = eval("ret")
        print(f"my_ret: {my_ret}")
    """
    for i in range(10):
        exec(f"def f_{i}(): return {i}")
    # Run functions f_0 to f_9
    for i in range(10):
        b = None
        exec(f"a = f_{i}()")
        exec(f"print(a)")
        b = eval("a")
        print(b)
    """
