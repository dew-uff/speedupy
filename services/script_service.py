from util import python_code_to_AST, get_script_path
from entities.Script import Script
from ASTSearcher import ASTSearcher

def create_script(script_name:str, experiment_base_dir:str) -> Script:
    script_path = get_script_path(script_name, experiment_base_dir)
    script_AST = python_code_to_AST(script_path)
    if(script_AST is None):
        raise RuntimeError

    script_ASTSearcher = ASTSearcher(script_AST)
    script_ASTSearcher.search()

    for function_name in script_ASTSearcher.functions:
        script_ASTSearcher.functions[function_name].qualname = function_name
    
    return Script(script_name, script_AST, script_ASTSearcher.import_commands, script_ASTSearcher.functions)