from typing import List
import ast
from entities.Experiment import Experiment
from entities.FunctionGraph import FunctionGraph
from entities.Script import Script
from services.FunctionCalledDetector import FunctionCalledDetector

class ScriptFunctionGraphCreator(ast.NodeVisitor):
    def __init__(self, main_script:Script, dependency_scripts_names:List[str], experiment:Experiment):
        self.__experiment = experiment
        self.__script = main_script
        self.__script_function_graph = FunctionGraph(main_script, dependency_scripts_names, experiment)
        self.__function_call_detector = FunctionCalledDetector(self.__script, self.__experiment)
        

    def create_function_graph(self) -> FunctionGraph:
        self.__current_function_name = ""
        self.__current_function = None
        self.visit(self.__script.AST)
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
        #Testing if this node represents a call to some function done inside another function
        if(self.__current_function_name != ""):
            function_called = None
            
            if(isinstance(node.func, ast.Name)):
                #In this case the function called can be either a function imported
                #with the command "from ... import ..." or a function declared by the
                #user in the file

                function_called_name = node.func.id
                function_called = self.__function_call_detector.find_function_called(function_called_name)
                
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

                function_called = self.__function_call_detector.find_function_called(function_called_name)
            
            if(function_called != None):
                self.__script_function_graph.add(self.__current_function, function_called)

        self.generic_visit(node)
