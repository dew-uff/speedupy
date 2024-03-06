import ast, os, importlib

from typing import List, Dict
from util import get_script_path
from entities.Script import Script
from entities.Experiment import Experiment
from setup_exp.services.ASTSearcherService import ASTSearcherService
from setup_exp.services.ScriptFunctionGraphCreatorService import ScriptFunctionGraphCreatorService
from services.function_service import decorate_function, execute_and_classify_function

def create_script(script_name:str, experiment_base_dir:str) -> Script:
    script_path = get_script_path(script_name, experiment_base_dir)
    script_AST = _python_code_to_AST(script_path)
    if(script_AST is None):
        raise RuntimeError

    script_ASTSearcher = ASTSearcherService(script_AST)
    script_ASTSearcher.search()

    for function_name in script_ASTSearcher.functions:
        script_ASTSearcher.functions[function_name].qualname = function_name
    
    return Script(script_name, script_AST, script_ASTSearcher.import_commands, script_ASTSearcher.functions)

def _python_code_to_AST(file_name:str) -> ast.Module:
    try:
        #Opening file
        file = open(file_name, "r")

    except:
        print("Error while trying to open file!")
        print("Check if the file exists!")
        return None

    else:
        try:
            #Generating AST from Python code
            return ast.parse(file.read())

        except:
            print("Error while trying to generate AST from the Python code!")
            print("Check if your Python script is correctly writen.")
            return None

def create_script_function_graph(main_script:Script, experiment:Experiment) -> None:
    u_def_imported_scripts = main_script.get_user_defined_imported_scripts(experiment.base_dir)
    __create_user_defined_imported_scripts_function_graphs(u_def_imported_scripts, experiment)
    script_function_graph = ScriptFunctionGraphCreatorService(main_script, u_def_imported_scripts, experiment).create_function_graph()
    main_script.function_graph = script_function_graph

def __create_user_defined_imported_scripts_function_graphs(u_def_imported_scripts:List[str], experiment:Experiment) -> None:
    for script_name in u_def_imported_scripts:
        create_script_function_graph(experiment.scripts[script_name], experiment)

def decorate_script_functions(script:Script) -> bool:
    """This function decorates all functions of a script that can be decorated with @maybe_deterministic. It returns True if at least one function was decorated. If no functions were marked with @maybe_deterministic, this function returns False."""
    script_decorated = False
    for function in script.functions.values():
        function_decorated = decorate_function(function)
        script_decorated = script_decorated or function_decorated
    return script_decorated

def add_decorator_import(script:Script, decorator_name:str) -> None:
    if _script_already_has_decorator_import(script, decorator_name): return
    current_folder = os.getcwd()
    imports = f"import sys\nsys.path.append('{current_folder}')\n"
    imports += f"from speedupy.speedupy import {decorator_name}"
    imports = ast.parse(imports)
    script.AST.body = imports.body + script.AST.body

def _script_already_has_decorator_import(script:Script, decorator_name:str) -> bool:
    for cmd in script.import_commands:
        if isinstance(cmd, ast.ImportFrom) and cmd.module == 'speedupy.speedupy' and cmd.level == 0:
            for alias in cmd.names:
                if alias.name == decorator_name: return True
    return False

def add_start_inference_engine_import(script:Script) -> None:
    #Replacing "from speedupy.intpy import execute_intpy" for 
    #          "from speedupy.function_inference_engine import start_inference_engine"
    script.AST.body.pop(3)
    import_command = ast.parse("from speedupy.function_inference_engine import start_inference_engine")
    script.AST.body.insert(3, import_command)

def overwrite_decorated_script(script:Script):        
    with open(script.name, 'wt') as f:
        f.write(ast.unparse(script.AST))

def classify_script_functions(script:Script, functions_2_hashes:Dict[str, str]) -> None:
    module_name = _get_module_name(script)
    module = importlib.import_module(module_name)
    for function in script.functions.values():
        execute_and_classify_function(module, function, functions_2_hashes)

def _get_module_name(script:Script) -> str:
    return script.name.replace(os.sep, ".").replace(".py", "")
