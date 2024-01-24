import ast, os, importlib

from typing import List, Dict, Union
from util import python_code_to_AST, get_script_path
from entities.Script import Script
from entities.Experiment import Experiment
from services.ASTSearcher import ASTSearcher
from services.ScriptFunctionGraphCreator import ScriptFunctionGraphCreator
from services.function_service import decorate_function, execute_and_classify_function
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

def decorate_script_functions_for_execution(script:Script) -> None:
    for function in script.functions.values():
        decorate_function(function)

def add_common_decorator_imports_for_execution(script:Script) -> None:
    current_folder = os.getcwd()
    imports = f"import sys\nsys.path.append('{current_folder}')\n"
    imports += "from speedupy.intpy import maybe_deterministic"
    imports = ast.parse(imports)
    script.AST.body = imports.body + script.AST.body

def add_execute_intpy_import(script:Script) -> None:
    import_command = ast.parse("from speedupy.intpy import execute_intpy")
    #Inserting import right after "from speedupy.intpy import maybe_deterministic"
    script.AST.body.insert(3, import_command)

def add_start_inference_engine_import(script:Script) -> None:
    #Replacing "from speedupy.intpy import execute_intpy" for 
    #          "from speedupy.function_inference_engine import start_inference_engine"
    script.AST.body.pop(3)
    import_command = ast.parse("from speedupy.function_inference_engine import start_inference_engine")
    script.AST.body.insert(3, import_command)

def copy_script(script:Script):        
    folders = os.path.dirname(script.name)
    temp_path = os.path.join(Constantes().TEMP_FOLDER, folders)
    os.makedirs(temp_path, exist_ok=True)
    with open(os.path.join(Constantes().TEMP_FOLDER, script.name), 'wt') as f:
        f.write(ast.unparse(script.AST))

def classify_script_functions(script:Script, functions_2_hashes:Dict[str, str]) -> None:
    module_name = _get_module_name(script)
    module = importlib.import_module(module_name)
    for function in script.functions.values():
        execute_and_classify_function(module, function, functions_2_hashes)

def _get_module_name(script:Script) -> str:
    return script.name.replace(os.sep, ".").replace(".py", "")
