import ast, os, importlib

from typing import Dict
from entities.Script import Script
from services.function_service import execute_and_classify_function

def add_start_inference_engine_import(script:Script) -> None:
    #Replacing "from speedupy.intpy import execute_intpy" for 
    #          "from speedupy.function_inference_engine import start_inference_engine"
    script.AST.body.pop(3)
    import_command = ast.parse("from speedupy.function_inference_engine import start_inference_engine")
    script.AST.body.insert(3, import_command)

def classify_script_functions(script:Script, functions_2_hashes:Dict[str, str]) -> None:
    module_name = _get_module_name(script)
    module = importlib.import_module(module_name)
    for function in script.functions.values():
        execute_and_classify_function(module, function, functions_2_hashes)

def _get_module_name(script:Script) -> str:
    return script.name.replace(os.sep, ".").replace(".py", "")
