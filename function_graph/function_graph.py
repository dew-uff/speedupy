import ast, os, os.path
from util import *
from ExperimentFunctionGraphCreatir import ExperimentFunctionGraphCreator
from typing import Set
from services.experiment_service import ExperimentService
def create_experiment_function_graph(self, user_script_path):
    experiment = ExperimentService(user_script_path)
    experimentFunctionGraphCreator = ExperimentFunctionGraphCreator(experiment)
    experimentFunctionGraphCreator.create_experiment_function_graph()
    return experimentFunctionGraphCreator.experiment_function_graph

def get_source_code_executed(function, function_graph):
    list_of_graph_vertices_not_yet_processed = []
    list_of_graph_vertices_already_processed = []
    source_codes_executed = []
    for current_function_def_node in function_graph:
        if(current_function_def_node.qualname == function.__qualname__):
            list_of_graph_vertices_not_yet_processed.append(current_function_def_node)
            break

    while(len(list_of_graph_vertices_not_yet_processed) > 0):
        current_vertice = list_of_graph_vertices_not_yet_processed.pop(0)

        source_codes_executed.append(ast.unparse(current_vertice))

        for linked_vertice in function_graph[current_vertice]:
            if(linked_vertice not in list_of_graph_vertices_not_yet_processed and
            linked_vertice not in list_of_graph_vertices_already_processed and
            linked_vertice != current_vertice):
                list_of_graph_vertices_not_yet_processed.append(linked_vertice)
        
        list_of_graph_vertices_already_processed.append(current_vertice)
    
    return "\n".join(source_codes_executed)
