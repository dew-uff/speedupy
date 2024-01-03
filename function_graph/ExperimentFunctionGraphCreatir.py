import ast
from util import is_an_user_defined_script

class ExperimentFunctionGraphCreator(ast.NodeVisitor):
    def __init__(self, experiment):
        self.__experiment = experiment
        self.__experiment_function_graph = {}

    
    def __initialize_script_function_graph(self, script, imported_scripts_names):
        script_function_graph = {}
        for imported_script_name in imported_scripts_names:
            script_function_graph.update(self.__experiment.scripts[imported_script_name].function_graph)
        for function in script.functions.values():
            script_function_graph[function] = set()
        return script_function_graph

    
    def create_experiment_function_graph(self):
        self.__experiment_function_graph = self.__create_script_function_graph("__main__")


    def __create_user_defined_imported_scripts_function_graphs(self, user_defined_imported_scripts):
        for user_defined_imported_script in user_defined_imported_scripts:
            self.__create_script_function_graph(user_defined_imported_script)


    def __create_script_function_graph(self, script_name):
        script = self.__experiment.scripts[script_name]

        user_defined_imported_scripts = script.get_user_defined_imported_scripts(self.__experiment.experiment_base_dir)
        
        self.__create_user_defined_imported_scripts_function_graphs(user_defined_imported_scripts)

        self.__script_function_graph = self.__initialize_script_function_graph(script, user_defined_imported_scripts)
        
        self.__current_script = script
        self.__current_function_name = ""
        self.__current_function = None
        self.visit(script.AST)
        
        script.function_graph = self.__script_function_graph
        return self.__script_function_graph


    def visit_ClassDef(self, node):
        """This function avoids that child nodes of a ClassDef node
        (ex.: class methods) be visited during search"""
        

    def visit_FunctionDef(self, node):
        previous_function_name = self.__current_function_name
        self.__current_function_name = node.name if self.__current_function_name == "" else self.__current_function_name + ".<locals>." + node.name
        previous_function = self.__current_function
        self.__current_function = node

        self.generic_visit(node)

        self.__current_function_name = previous_function_name
        self.__current_function = previous_function
    
    
    def visit_Call(self, node):
        def find_possible_functions_called(function_called_name):
            possible_functions_called = {}
            if(function_called_name.find(".") == -1):
                for function_name in self.__current_script.functions:
                    if(self.__current_script.functions[function_name].name == function_called_name):
                        possible_functions_called[function_name] = self.__current_script.functions[function_name]
                                
                import_command = self.__current_script.get_import_command_of_function(function_called_name)
                if(import_command is None):
                    return possible_functions_called

                imported_script_name = self.__current_script.import_command_to_imported_scripts_names(import_command)[0]
                if(not is_an_user_defined_script(imported_script_name, self.__experiment.experiment_base_dir)):
                    return possible_functions_called
                
                original_imported_function_name = self.__current_script.get_original_name_of_function_imported_with_import_from(import_command, function_called_name)
                try:
                    possible_functions_called[original_imported_function_name] = self.__experiment.scripts[imported_script_name].functions[original_imported_function_name]
                except:
                    #In this case the function called is a constructor to a class that was imported to the script
                    pass
                
            else:
                import_command = self.__current_script.get_import_command_of_function(function_called_name)
                if(import_command is None):
                    return possible_functions_called

                original_imported_script_name = self.__current_script.get_original_name_of_script_imported_with_import(import_command, function_called_name)
                
                imported_script_name = self.__current_script.script_name_to_script_path(original_imported_script_name)
                if(not is_an_user_defined_script(imported_script_name, self.__experiment.experiment_base_dir)):
                    return possible_functions_called
                
                possible_functions_called[function_called_name[function_called_name.rfind(".") + 1:]] = self.__experiment.scripts[imported_script_name].functions[function_called_name[function_called_name.rfind(".") + 1:]]

            return possible_functions_called


        def find_function_called(function_called_name, possible_functions_called):
            number_of_possible_functions_called = len(possible_functions_called)
            if(number_of_possible_functions_called == 0):
                return None
            elif(number_of_possible_functions_called == 1):
                return list(possible_functions_called.values())[0]
            else:
                #In this case there are two functions defined in the script
                #with the same name
                #Finding function defined in the smaller scope
                function_called = None
                function_called_name_prefix = self.__current_function_name + ".<locals>."
                while(function_called == None):
                    for possible_function_called_name in possible_functions_called:
                        if(function_called_name_prefix + function_called_name == possible_function_called_name):
                            function_called = self.__current_script.functions[possible_function_called_name]
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
                return function_called
        
        #Testing if this node represents a call to some function done inside another function
        if(self.__current_function_name != ""):
            function_called = None
            
            if(isinstance(node.func, ast.Name)):
                #In this case the function called can be either a function imported
                #with the command "from ... im  port ..." or a function declared by the
                #user in the file

                function_called_name = node.func.id
                possible_functions_called = find_possible_functions_called(function_called_name)
                function_called = find_function_called(function_called_name, possible_functions_called)
            
            elif(isinstance(node.func, ast.Attribute)):
                #In this case the function called is a function imported with the command
                #"import ..."

                #Building the name of the function called
                current_node = node.func
                function_called_name_parts = []
                while(isinstance(current_node, ast.Attribute)):
                    function_called_name_parts.append(current_node.attr)
                    current_node = current_node.value
                function_called_name_parts.append(current_node.id)

                function_called_name_parts.reverse()
                function_called_name = ".".join(function_called_name_parts)

                possible_functions_called = find_possible_functions_called(function_called_name)
                function_called = find_function_called(function_called_name, possible_functions_called)
            
            if(function_called != None):
                self.__script_function_graph[self.__current_function].add(function_called)

        self.generic_visit(node)


    @property
    def experiment_function_graph(self):
        return self.__experiment_function_graph
