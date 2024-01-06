from typing import Set, Union, List, Optional
import os, ast

def python_code_to_AST(file_name:str) -> ast.Module:
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


def get_script_path(script_name:str, experiment_base_dir:str) -> str:
    return os.path.join(experiment_base_dir, script_name)


def is_an_user_defined_script(imported_script:str, experiment_base_dir:str) -> bool:
    return os.path.exists(get_script_path(imported_script, experiment_base_dir)) and imported_script.find("intpy") == -1


def get_all_init_scripts_implicitly_imported(imported_script:str, experiment_base_dir:str) -> Set[str]:
    init_scripts_implicitly_imported = set()
    if(imported_script.rfind(os.sep) != -1):
        current_init_script_path = imported_script[0:imported_script.rfind(os.sep) + 1] + "__init__.py"
        while(current_init_script_path != "__init__.py"):
            if(os.path.exists(get_script_path(current_init_script_path, experiment_base_dir))):
                init_scripts_implicitly_imported.add(current_init_script_path)
            current_init_script_path = current_init_script_path.split(os.sep)
            current_init_script_path.pop(-2)
            current_init_script_path = os.sep.join(current_init_script_path)
    return init_scripts_implicitly_imported

def import_command_to_imported_scripts_names(import_command: Union[ast.Import, ast.ImportFrom], main_script_dir:str) -> List[str]:
    imported_scripts_names = []
    if(isinstance(import_command, ast.Import)):
        for alias in import_command.names:
            imported_scripts_names.append(script_name_to_script_path(alias.name, main_script_dir))

    elif(isinstance(import_command, ast.ImportFrom)):
        imported_script_name = import_command.level * "." + import_command.module if import_command.module is not None else import_command.level * "."
        imported_scripts_names.append(script_name_to_script_path(imported_script_name, main_script_dir))
        
    return imported_scripts_names

def script_name_to_script_path(imported_script_name:str, main_script_dir:str) -> str:
    script_path = imported_script_name[0]
    for i in range(1, len(imported_script_name), 1):
        letter = imported_script_name[i]
        if((letter == "." and script_path[-1] != ".") or
        (letter != "." and script_path[-1] == ".")):
            script_path += os.sep + letter
        else:
            script_path += letter
    script_path += ".py" if script_path[-1] != "." else os.sep + "__init__.py"
    return os.path.normpath(os.path.join(main_script_dir, script_path))


#MAYBE IN THE FUTURE "get_original_name_of_script_imported_with_import" AND 
#"get_original_name_of_function_imported_with_import_from" CAN BE COLLAPSED
#IN ONE FUNCTION
def get_original_name_of_script_imported_with_import(import_command:ast.Import, function_name:str) -> Optional[str]:
    script_name = function_name[:function_name.rfind(".")]
    for alias in import_command.names:
        script_imported_name = alias.asname if alias.asname is not None else alias.name
        if(script_imported_name == script_name):
            return alias.name
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
        script_name = function_name[:function_name.rfind(".")]
        for import_command in import_commands:
            if(isinstance(import_command, ast.Import)):
                for alias in import_command.names:
                    script_imported_name = alias.asname if alias.asname is not None else alias.name
                    if(script_imported_name == script_name):
                        return import_command
    return None