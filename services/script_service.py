import ast

from typing import List, Dict
from util import python_code_to_AST, get_script_path
from entities.Script import Script
from entities.Experiment import Experiment
from services.ASTSearcher import ASTSearcher
from services.ScriptFunctionGraphCreator import ScriptFunctionGraphCreator
from services.function_service import decorate_function
from services.function_inference_service import FunctionClassification

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

def create_script_function_graph(script_name:str, experiment:Experiment) -> None:
    main_script = experiment.scripts[script_name]
    u_def_imported_scripts = main_script.get_user_defined_imported_scripts(experiment.base_dir)
    __create_user_defined_imported_scripts_function_graphs(u_def_imported_scripts, experiment)
    script_function_graph = ScriptFunctionGraphCreator(main_script, u_def_imported_scripts, experiment).create_function_graph()
    main_script.function_graph = script_function_graph

def __create_user_defined_imported_scripts_function_graphs(u_def_imported_scripts:List[str], experiment:Experiment) -> None:
    for script in u_def_imported_scripts:
        create_script_function_graph(script, experiment)

def decorate_script_functions(script:Script, classified_functions:Dict[str, FunctionClassification]) -> None:
    for function in script.functions.values():
        decorate_function(function, script.function_graph, classified_functions)

def copy_script(script:Script):
    for imp in script.import_commands:
        pass

    script.name = '__main__temp.py' if script.name == '__main__' else script.name.replace(".py", "_temp.py")
    with open(script.name, "wt") as f:
        f.write(ast.unparse(script.AST))