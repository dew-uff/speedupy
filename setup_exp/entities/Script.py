from typing import List, Optional
import ast, os
from util import is_an_user_defined_script, import_command_to_imported_scripts_names

class Script():
    def __init__(self, name = "", AST = None, import_commands = set(), functions = {}, function_graph = None):
        self.__name = name
        self.__AST = AST
        self.__import_commands = import_commands
        self.__functions = functions
        self.__function_graph = function_graph

    def get_user_defined_imported_scripts(self, experiment_base_dir:str):
        imported_scripts = self.get_imported_scripts()
        user_defined_imported_scripts = []
        for imported_script in imported_scripts:
            if is_an_user_defined_script(imported_script, experiment_base_dir):
                user_defined_imported_scripts.append(imported_script)
        return user_defined_imported_scripts
    
    def get_imported_scripts(self) -> List[str]:
        imported_scripts = []
        for import_command in self.__import_commands:
            imported_scripts += import_command_to_imported_scripts_names(import_command, os.path.dirname(self.__name))
        return imported_scripts


    def get_function(self, function_name:str) -> Optional[ast.FunctionDef]:
        try:
            return self.__functions[function_name]
        except KeyError:
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
