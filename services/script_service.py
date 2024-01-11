import ast, os, re

from typing import List, Dict, Union
from util import python_code_to_AST, get_script_path, script_name_to_script_path, is_an_user_defined_script
from entities.Script import Script
from entities.Experiment import Experiment
from services.ASTSearcher import ASTSearcher
from services.ScriptFunctionGraphCreator import ScriptFunctionGraphCreator
from services.function_service import decorate_function
from services.function_inference_service import FunctionClassification
from constantes import Constantes

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

def create_script_function_graph(main_script:Script, experiment:Experiment) -> None:
    u_def_imported_scripts = main_script.get_user_defined_imported_scripts(experiment.base_dir)
    __create_user_defined_imported_scripts_function_graphs(u_def_imported_scripts, experiment)
    script_function_graph = ScriptFunctionGraphCreator(main_script, u_def_imported_scripts, experiment).create_function_graph()
    main_script.function_graph = script_function_graph

def __create_user_defined_imported_scripts_function_graphs(u_def_imported_scripts:List[str], experiment:Experiment) -> None:
    for script_name in u_def_imported_scripts:
        create_script_function_graph(experiment.scripts[script_name], experiment)

def decorate_script_functions(script:Script, classified_functions:Dict[str, FunctionClassification], functions2hashes:Dict[str, str]) -> None:
    for function in script.functions.values():
        decorate_function(function, classified_functions, functions2hashes)

def add_decorator_imports(script:Script) -> None:
    current_folder = os.getcwd()
    imports = f"import sys\nsys.path.append('{current_folder}')\n"
    imports += "from speedupy.intpy import execute_intpy, deterministic, maybe_deterministic, collect_metadata"
    imports = ast.parse(imports)
    script.AST.body = imports.body + script.AST.body

def copy_script(script:Script):        
    folders = os.path.dirname(script.name)
    temp_path = os.path.join(Constantes().TEMP_FOLDER, folders)
    os.makedirs(temp_path, exist_ok=True)
    with open(os.path.join(Constantes().TEMP_FOLDER, script.name), 'wt') as f:
        f.write(ast.unparse(script.AST))
