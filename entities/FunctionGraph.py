import ast
from util import *
from typing import Union, List, Callable
from entities.Script import Script
from entities.Experiment import Experiment

class FunctionGraph():
    def __init__(self, main_script:Script, dependency_scripts_names:List[str], experiment:Experiment):
        self.__graph = {}
        for name in dependency_scripts_names:
            dep_script = experiment.scripts[name]
            self.__graph.update(dep_script.function_graph)
        for function in main_script.functions.values():
            self.__graph[function] = set()
    
    def add(self, caller_function, function_called):
        self.__graph[caller_function].add(function_called)
    
    def get_source_code_executed(self, function:Union[Callable, ast.FunctionDef]) -> str:
        list_of_graph_vertices_not_yet_processed = []
        list_of_graph_vertices_already_processed = []
        source_codes_executed = []
        for current_function_def_node in self.__graph:
            if(isinstance(function, Callable) and current_function_def_node.qualname == function.__qualname__) or \
              (isinstance(function, ast.FunctionDef) and current_function_def_node == function):
                list_of_graph_vertices_not_yet_processed.append(current_function_def_node)
                break

        while(len(list_of_graph_vertices_not_yet_processed) > 0):
            current_vertice = list_of_graph_vertices_not_yet_processed.pop(0)

            source_codes_executed.append(ast.unparse(current_vertice))

            for linked_vertice in self.__graph[current_vertice]:
                if(linked_vertice not in list_of_graph_vertices_not_yet_processed and
                linked_vertice not in list_of_graph_vertices_already_processed and
                linked_vertice != current_vertice):
                    list_of_graph_vertices_not_yet_processed.append(linked_vertice)
            
            list_of_graph_vertices_already_processed.append(current_vertice)
        
        return "\n".join(source_codes_executed)
