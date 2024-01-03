import ast, os
from util import is_an_user_defined_script

class Script():
    def __init__(self, name = "", AST = None, import_commands = set(), functions = {}, function_graph = None):
        self.__name = name
        self.__AST = AST
        self.__import_commands = import_commands
        self.__functions = functions
        self.__function_graph = function_graph


    def script_name_to_script_path(self, script_name):
            script_path = script_name[0]
            for i in range(1, len(script_name), 1):
                letter = script_name[i]
                if((letter == "." and script_path[-1] != ".") or
                (letter != "." and script_path[-1] == ".")):
                    script_path += os.sep + letter
                else:
                    script_path += letter
            script_path += ".py" if script_path[-1] != "." else os.sep + "__init__.py"
            return os.path.normpath(os.path.join(os.path.dirname(self.__name), script_path))


    def import_command_to_imported_scripts_names(self, import_command):
        imported_scripts_names = []
        if(isinstance(import_command, ast.Import)):
            for alias in import_command.names:
                imported_scripts_names.append(self.script_name_to_script_path(alias.name))

        elif(isinstance(import_command, ast.ImportFrom)):
            imported_script_name = import_command.level * "." + import_command.module if import_command.module is not None else import_command.level * "."
            imported_scripts_names.append(self.script_name_to_script_path(imported_script_name))
            
        return imported_scripts_names

    
    def get_imported_scripts(self):
        imported_scripts = []
        for import_command in self.__import_commands:
            imported_scripts += self.import_command_to_imported_scripts_names(import_command)
        return imported_scripts

    
    def get_user_defined_imported_scripts(self, experiment_base_dir):
        imported_scripts = self.get_imported_scripts()
        user_defined_imported_scripts = []
        for imported_script in imported_scripts:
            if is_an_user_defined_script(imported_script, experiment_base_dir):
                user_defined_imported_scripts.append(imported_script)
        return user_defined_imported_scripts

    
    def get_import_command_of_function(self, function_name):
        if(function_name.find(".") == -1):
            for import_command in self.__import_commands:
                if(isinstance(import_command, ast.ImportFrom)):
                    for alias in import_command.names:
                        function_imported_name = alias.asname if alias.asname is not None else alias.name
                        if(function_imported_name == function_name):
                            return import_command
        else:
            script_name = function_name[:function_name.rfind(".")]
            for import_command in self.__import_commands:
                if(isinstance(import_command, ast.Import)):
                    for alias in import_command.names:
                        script_imported_name = alias.asname if alias.asname is not None else alias.name
                        if(script_imported_name == script_name):
                            return import_command
        return None

    #MAYBE IN THE FUTURE "get_original_name_of_script_imported_with_import" AND 
    #"get_original_name_of_function_imported_with_import_from" CAN BE COLLAPSED
    #IN ONE FUNCTION
    def get_original_name_of_script_imported_with_import(self, import_command, function_name):
        script_name = function_name[:function_name.rfind(".")]
        for alias in import_command.names:
            script_imported_name = alias.asname if alias.asname is not None else alias.name
            if(script_imported_name == script_name):
                return alias.name
        return None

    
    def get_original_name_of_function_imported_with_import_from(self, import_from_command, function_name):
        for alias in import_from_command.names:
            function_imported_name = alias.asname if alias.asname is not None else alias.name
            if(function_imported_name == function_name):
                return alias.name
        return None

    
    def get_function(self, function_name):
        if(function_name in self.__functions):
            return self.__functions[function_name]
        return None


    ###DEBUG####
    def print(self):
        print("#####SCRIPT#####")
        print("Name:", self.__name)
        print("AST:", self.__AST)
        print("Import Commands:", self.__import_commands)
        print("Functions:", self.__functions)
        print("Function Graph:")
        if(self.__function_graph is not None):
            for function in self.__function_graph:
                print(3*" ", function.qualname, function)
                for link in self.__function_graph[function]:
                    print(6*" ", link.qualname, link)


    @property
    def name(self):
        return self.__name
    

    @name.setter
    def name(self, name):
        self.__name = name


    @property
    def AST(self):
        return self.__AST


    @AST.setter
    def AST(self, AST):
        self.__AST = AST


    @property
    def import_commands(self):
        return self.__import_commands
    

    @import_commands.setter
    def import_commands(self, import_commands):
        self.__import_commands = import_commands


    @property
    def functions(self):
        return self.__functions


    @functions.setter
    def functions(self, functions):
        self.__functions = functions
    

    @property
    def function_graph(self):
        return self.__function_graph
 

    @function_graph.setter
    def function_graph(self, function_graph):
        self.__function_graph = function_graph
