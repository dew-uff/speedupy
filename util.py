from typing import Set, Union, List, Optional, Dict
import os, ast, json
from copy import deepcopy
from constantes import Constantes

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

def save_json_file(data:Dict, filename:str) -> None:
    with open(filename, "wt") as file:
        json.dump(data, file)

def get_content_json_file(filename:str) -> Dict:
    with open(filename) as file:
        return json.load(file)

def _get_src_and_dest_to_copy_to_temp_folder(path:str, is_file:bool) -> None:
    if is_file:
        src = path
        file_folder = os.path.dirname(src)
        dest = os.path.join(Constantes().TEMP_FOLDER, file_folder)
    else:
        src = os.path.join(path, "*")
        dest = os.path.join(Constantes().TEMP_FOLDER, path)
    return src, dest

def copy_to_temp_folder(src:str, is_file:bool) -> None:
    src, dest = _get_src_and_dest_to_copy_to_temp_folder(src, is_file)
    os.makedirs(dest, exist_ok=True)
    os.system(f'cp -r {src} {dest}')

def _get_src_and_dest_to_copy_from_temp_folder(path:str, is_file:bool) -> None:
    if is_file:
        src = os.path.join(Constantes().TEMP_FOLDER, path)
        dest = os.path.dirname(path) if os.path.dirname(path) != '' else './'
    else:
        src = os.path.join(Constantes().TEMP_FOLDER, path, '*')
        dest = path
    return src, dest

def copy_from_temp_folder(dest:str, is_file:bool) -> None:
    src, dest = _get_src_and_dest_to_copy_from_temp_folder(dest, is_file)
    os.makedirs(dest, exist_ok=True)
    os.system(f'cp -r {src} {dest}')
