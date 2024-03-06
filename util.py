from typing import Union, List, Dict
import os, ast, json, pickle
from copy import deepcopy

def is_an_user_defined_script(imported_script:str, experiment_base_dir:str) -> bool:
    return os.path.exists(get_script_path(imported_script, experiment_base_dir)) and imported_script.find("intpy") == -1

def get_script_path(script_name:str, experiment_base_dir:str) -> str:
    return os.path.join(experiment_base_dir, script_name)

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
    script_path = __convert_relative_importFrom_dots_to_valid_path(script_path)
    script_path += ".py" if script_path[-1] != "." else os.sep + "__init__.py"
    return os.path.normpath(os.path.join(main_script_dir, script_path))

def __convert_relative_importFrom_dots_to_valid_path(script_path):
    new_script_path = deepcopy(script_path)
    start = -1
    for i in range(len(script_path)):
        letter = script_path[i]
        if letter == '.' and start == -1:
            start = i
        if letter != '.' and start != -1:
            end = i
            num_points = end - start
            if num_points > 1:
                new_script_path = new_script_path.replace(num_points*'.', '.' + (num_points-1)*'/..', 1)
            start = -1
    return new_script_path

def save_json_file(data:Dict, filename:str) -> None:
    with open(filename, "wt") as file:
        json.dump(data, file)

def get_content_json_file(filename:str) -> Dict:
    with open(filename) as file:
        return json.load(file)
    
def deserialize_from_file(filename:str):
    with open(filename, 'rb') as file:
        return pickle.load(file)

def serialize_to_file(obj, filename:str):
    with open(filename, 'wb') as file:
        return pickle.dump(obj, file)
