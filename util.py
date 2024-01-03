import os, ast

def python_code_to_AST(file_name):
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


def get_script_path(script_name, experiment_base_dir):
    return os.path.join(experiment_base_dir, script_name)


def is_an_user_defined_script(imported_script, experiment_base_dir):
    return os.path.exists(get_script_path(imported_script, experiment_base_dir)) and imported_script.find("intpy") == -1

def get_all_init_scripts_implicitly_imported(imported_script:str, experiment_base_dir:str) -> Set(str):
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