import ast
from typing import Dict
from data_access import _get_id
from services.function_inference_service import FunctionClassification
from entities.FunctionGraph import FunctionGraph

def decorate_function(function:ast.FunctionDef, function_graph:FunctionGraph, classified_functions:Dict[str, FunctionClassification]) -> None:
    fun_source = function_graph.get_source_code_executed(function)
    id = _get_id(fun_source)
    try:
        if not is_main_function(function) and classified_functions[id] == FunctionClassification.CACHE:
            function.decorator_list.append(ast.Name("deterministic", ast.Load()))
    except KeyError:
        function.decorator_list.append(ast.Name("collect_metadata", ast.Load()))    

def is_main_function(function:ast.FunctionDef) -> bool:
    for decorator in function.decorator_list:
        if isinstance(decorator, ast.Call) and decorator.func.id == "initialize_intpy":
            return True        
    return False
