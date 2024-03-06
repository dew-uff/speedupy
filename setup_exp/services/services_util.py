from typing import Union, Optional
import ast

#MAYBE IN THE FUTURE "get_original_name_of_script_imported_with_import" AND 
#"get_original_name_of_function_imported_with_import_from" CAN BE COLLAPSED
#IN ONE FUNCTION
def get_original_name_of_script_imported(import_command:Union[ast.Import, ast.ImportFrom], function_name:str) -> Optional[str]:
    if isinstance(import_command, ast.Import):#"import SCRIPT (........) SCRIPT.FUNCTION()"
        script_name = function_name[:function_name.rfind(".")]
    elif isinstance(import_command, ast.ImportFrom): #"from ... import SCRIPT (........) SCRIPT.FUNCTION()"
        script_name = function_name[:function_name.find(".")]
    for alias in import_command.names:
        script_imported_name = alias.asname if alias.asname is not None else alias.name
        if(script_imported_name == script_name):
            if isinstance(import_command, ast.Import):
                return alias.name
            elif isinstance(import_command, ast.ImportFrom):
                script_prefix_name = import_command.level * "." + import_command.module + "." if import_command.module is not None else import_command.level * "."
                return script_prefix_name + alias.name
    return None

def get_original_name_of_function_imported_with_import_from(import_from_command:ast.ImportFrom, function_name:str) -> Optional[str]:
    for alias in import_from_command.names:
        function_imported_name = alias.asname if alias.asname is not None else alias.name
        if(function_imported_name == function_name):
            return alias.name
    return None

def get_import_command_of_function(function_name:str, import_commands:Union[ast.Import, ast.ImportFrom]) -> Optional[Union[ast.Import, ast.ImportFrom]]:
    if(function_name.find(".") == -1):
        for import_command in import_commands:
            if(isinstance(import_command, ast.ImportFrom)):
                for alias in import_command.names:
                    function_imported_name = alias.asname if alias.asname is not None else alias.name
                    if(function_imported_name == function_name):
                        return import_command
    else:
        script_name_for_ast_import = function_name[:function_name.rfind(".")]
        script_name_for_ast_importFrom = function_name[:function_name.find(".")]
        for import_command in import_commands:
            if(isinstance(import_command, ast.Import)): #Using "import ..." to import a module
                script_name = script_name_for_ast_import
            elif(isinstance(import_command, ast.ImportFrom)): #Using "from ... import ..." to import a module
                script_name = script_name_for_ast_importFrom
            
            for alias in import_command.names:
                script_imported_name = alias.asname if alias.asname is not None else alias.name
                if(script_imported_name == script_name):
                    return import_command
    return None
