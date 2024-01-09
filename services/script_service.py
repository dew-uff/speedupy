import ast, os, re

from typing import List, Dict, Union
from util import python_code_to_AST, get_script_path, script_name_to_script_path, is_an_user_defined_script
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

def copy_script(script:Script, exp_base_dir:str):
    __update_import_command_paths(script, exp_base_dir)
    script.name = __get_script_temp_path(script.name)
    if __script_is_inside_folder(script.name):
        __create_script_path(script.name)
        
    with open(script.name, "wt") as f:
        f.write(ast.unparse(script.AST))

def __update_import_command_paths(script:Script, exp_base_dir:str):
    for imp in script.import_commands:
        if isinstance(imp, ast.Import):
            __update_ast_Import_command_paths(script, imp, exp_base_dir)
        elif isinstance(imp, ast.ImportFrom):
            __update_ast_ImportFrom_command_paths(script, imp, exp_base_dir)

def __update_ast_Import_command_paths(script:Script, import_command:ast.Import, exp_base_dir:str) -> None:
    for alias in import_command.names:
        if __path_need_to_be_updated(alias.name, os.path.dirname(script.name), exp_base_dir):
            alias.name = get_updated_path(alias.name)

def __path_need_to_be_updated(imported_script_path:str, main_script_folder:str, exp_base_dir:str) -> bool:
    imported_script_path = script_name_to_script_path(imported_script_path, main_script_folder)
    return is_an_user_defined_script(imported_script_path, exp_base_dir)

def get_updated_path(old_path:str) -> str:
    new_path = old_path.replace(".", "_temp.")
    return new_path + "_temp"

def __update_ast_ImportFrom_command_paths(script:Script, import_command:ast.ImportFrom, exp_base_dir:str) -> None:
    imported_script_name = import_command.level * "." + import_command.module if import_command.module is not None else import_command.level * "."
    if __path_need_to_be_updated(imported_script_name, os.path.dirname(script.name), exp_base_dir):
        #from .... import FUNCTION
        if import_command.module is not None:
            import_command.module = get_updated_path(import_command.module)
    else:
        #Checking if script is using "from .... import MODULE (........) MODULE.FUNCTION()"
        for alias in import_command.names:
            if imported_script_name[-1] == '.': #imported_script_name is only a relative path
                sep = ''
            else:
                sep = '.'
            complete_path = sep.join([imported_script_name, alias.name])
            if __path_need_to_be_updated(complete_path, os.path.dirname(script.name), exp_base_dir):
                if import_command.module is not None:
                    import_command.module = get_updated_path(import_command.module)
                alias.name += "_temp"

def __get_script_temp_path(script_path:str) -> str:
    folders, script_name = os.path.split(script_path)
    if script_name != '__init__.py':
        script_name = script_name.replace(".py", "_temp.py")
    if __script_is_inside_folder(script_path):
        temp_path = (os.sep).join([f"{fol}_temp" for fol in folders.split(os.sep)])
        return os.path.join(temp_path, script_name)
    else:
        return script_name

def __script_is_inside_folder(script_path:str) -> bool:
    return script_path.find(os.sep) != -1

def __create_script_path(script_path:str) -> None:
    script_folder = os.path.dirname(script_path)
    os.makedirs(script_folder)
