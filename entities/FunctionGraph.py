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
            self.__graph.update(dep_script.function_graph.graph)
        for function in main_script.functions.values():
            self.__graph[function] = []
    
    def add(self, caller_function, function_called):
        self.__graph[caller_function].append(function_called)
    
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
    
    def get_source_code_executed_by_graph_node(self, function:ast.FunctionDef) -> str:
        vertices_not_yet_processed = []
        processed_vertices = []
        source_codes_executed = []
        
        vertices_not_yet_processed.append(function)
        while(len(vertices_not_yet_processed) > 0):
            current_vertice = vertices_not_yet_processed.pop(0)
            source_codes_executed.append(ast.unparse(current_vertice))
            processed_vertices.append(current_vertice)
            for linked_vertice in self.__graph[current_vertice]:
                if(linked_vertice not in vertices_not_yet_processed and
                   linked_vertice not in processed_vertices):
                    vertices_not_yet_processed.append(linked_vertice)
        return "\n".join(source_codes_executed)

    @property
    def graph(self):
        return self.__graph
