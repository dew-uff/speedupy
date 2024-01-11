import ast
from typing import Dict
from services.function_inference_service import FunctionClassification

def decorate_function(function:ast.FunctionDef, classified_functions:Dict[str, FunctionClassification], functions2hashes:Dict[str, str]) -> None:
    if is_main_function(function):
        return
    id = functions2hashes[function.qualname]
    try:
        if classified_functions[id] == FunctionClassification.CACHE:
            function.decorator_list.append(ast.Name("deterministic", ast.Load()))
        elif classified_functions[id] == FunctionClassification.MAYBE_CACHE:
            function.decorator_list.append(ast.Name("maybe_deterministic", ast.Load()))
    except KeyError:
        function.decorator_list.append(ast.Name("collect_metadata", ast.Load()))

def is_main_function(function:ast.FunctionDef) -> bool:
    for decorator in function.decorator_list:
        if isinstance(decorator, ast.Call) and decorator.func.id == "initialize_intpy":
            return True
    return False
