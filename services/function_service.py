from typing import List, Dict, Union, Tuple, Optional
import ast, pickle
from typing import Dict, Union
from services.function_inference_service import FunctionClassification
from constantes import Constantes

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
    # func_calls = get_all_func_calls_saved_as_metadata(func_hash)

#TODO
# def get_all_func_calls_saved_as_metadata(func_hash:str) -> List[str]:
#     sql = "SELECT return_value, execution_time, parameter_value, parameter_name, parameter_position \
#            FROM METADATA JOIN FUNCTION_PARAMS ON METADATA.id = FUNCTION_PARAMS.metadata_id\
#            WHERE function_hash = ?)"
#     res = Constantes().CONEXAO_BANCO.executarComandoSQLSelect("SELECT.")
#     func_call_hashes = []
#     for args, kwargs in res:
#         hash = data_access.get_id(func_hash, args, kwargs)
#         func_call_hashes.append(hash)
#     return func_call_hashes


class FunctionCall():
    def __init__(self, function_hash, args, kwargs):
        self.__function_hash = function_hash
        self.__args = args
        self.__kwargs = kwargs
        
