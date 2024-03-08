from typing import Union
import ast

def decorate_main_function(main_function:ast.FunctionDef) -> None:
    for decorator in main_function.decorator_list:
        if _is_initialize_speedupy_decorator(decorator): return
    main_function.decorator_list.append(ast.Name(id='initialize_speedupy', ctx=ast.Load()))

def decorate_function(function:ast.FunctionDef) -> bool:
    """This function checks if the function received can be decorated with @maybe_deterministic. If it is possible to do so, the function is decorated and True is returned. If the function cannot be decorated this function returns False."""
    func_decorated = _is_already_decorated(function)
    if not func_decorated:
        function.decorator_list.append(ast.Name("maybe_deterministic", ast.Load()))
    return not func_decorated

def _is_already_decorated(function:ast.FunctionDef) -> bool:
    for decorator in function.decorator_list:
        if _is_initialize_speedupy_decorator(decorator) or \
           _is_common_speedupy_decorator(decorator):
            return True
    return False

def _is_initialize_speedupy_decorator(decorator:Union[ast.Call, ast.Name]) -> bool:
    return isinstance(decorator, ast.Name) and \
           decorator.id == "initialize_speedupy"

def _is_common_speedupy_decorator(decorator:Union[ast.Call, ast.Name]) -> bool:
    return isinstance(decorator, ast.Name) and \
           decorator.id in ["deterministic", "maybe_deterministic"]
