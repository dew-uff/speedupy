import os.path

from entities.Experiment import Experiment
from util import is_an_user_defined_script, script_name_to_script_path, import_command_to_imported_scripts_names, get_original_name_of_function_imported_with_import_from, get_original_name_of_script_imported_with_import, get_import_command_of_function
from entities.Script import Script

class FunctionCalledDetector():
    def __init__(self, script:Script, experiment:Experiment):
        self.__script = script
        self.__experiment = experiment
    
    def find_function_called(self, function_called_name:str):
        self.__function_called_name = function_called_name
        self.__find_possible_functions_called()
        self.__find_which_function_was_called()
        return self.__function_called

    def __find_possible_functions_called(self):
        self.__possible_functions_called = {}
        if(self.__function_called_has_simple_name()):
            self.__find_possible_simple_name_functions_declared_inside_script()
            self.__find_possible_simple_name_functions_imported_by_script()
        else:
            self.__find_possible_compose_name_functions_imported_by_script()
    
    def __function_called_has_simple_name(self) -> bool:
        return self.__function_called_name.find(".") == -1

    def __find_possible_simple_name_functions_declared_inside_script(self):
        for function_name in self.__script.functions:
            if(self.__script.functions[function_name].name == self.__function_called_name):
                self.__possible_functions_called[function_name] = self.__script.functions[function_name]
    
    def __find_possible_simple_name_functions_imported_by_script(self):
        import_command = get_import_command_of_function(self.__function_called_name, self.__script.import_commands)
        if(import_command is None):
            #No import command could have imported this function
            return

        imported_script_name = import_command_to_imported_scripts_names(import_command, os.path.dirname(self.__script.name))[0]
        if(not is_an_user_defined_script(imported_script_name, self.__experiment.base_dir)):
            #Script imported is not defined by the user, so function will never be cached
            return
        
        original_imported_function_name = get_original_name_of_function_imported_with_import_from(import_command, self.__function_called_name)
        try:
            self.__possible_functions_called[original_imported_function_name] = self.__experiment.scripts[imported_script_name].functions[original_imported_function_name]
        except:
            #In this case the function called is a constructor to a class that was imported to the script
            pass
    
    def __find_possible_compose_name_functions_imported_by_script(self):
        import_command = get_import_command_of_function(self.__function_called_name, self.__script.import_commands)
        if(import_command is None):
            #No import command could have imported this function
            return

        original_imported_script_name = get_original_name_of_script_imported_with_import(import_command, self.__function_called_name)
        
        imported_script_name = script_name_to_script_path(original_imported_script_name, os.path.dirname(self.__script.name))
        if(not is_an_user_defined_script(imported_script_name, self.__experiment.base_dir)):
            #Script imported is not defined by the user, so function will never be cached
            return
        
        func_last_name = self.__function_called_name[self.__function_called_name.rfind(".") + 1:]
        self.__possible_functions_called[func_last_name] = self.__experiment.scripts[imported_script_name].functions[func_last_name]

    def __find_which_function_was_called(self):
        self.__function_called = None
        number_of_possible_functions_called = len(self.__possible_functions_called)
        if(number_of_possible_functions_called == 0):
            return
        elif(number_of_possible_functions_called == 1):
            self.__function_called = list(self.__possible_functions_called.values())[0]
            return 
        else:
            #In this case there are two functions defined in the script
            #with the same name
            #Finding function defined in the smaller scope
            function_called_name_prefix = self.__current_function_name + ".<locals>."
            while(self.__function_called == None):
                for possible_func_called_name in self.__possible_functions_called:
                    if(function_called_name_prefix + self.__function_called_name == possible_func_called_name):
                        self.__function_called = self.__script.functions[possible_func_called_name]
                        break
                
                if(function_called_name_prefix == ""):
                    break

                #The string in "function_called_name_prefix" always ends in a dot (".<locals>.")
                #Hence, the last element of "function_called_name_prefix.split('.<locals>.')" will
                #always be an empty string ("")
                if(len(function_called_name_prefix.split(".<locals>.")) > 2):
                    function_called_name_prefix = function_called_name_prefix.split(".<locals>.")
                    function_called_name_prefix.pop(-2)
                    function_called_name_prefix = ".<locals>.".join(function_called_name_prefix)
                else:
                    function_called_name_prefix = ""
