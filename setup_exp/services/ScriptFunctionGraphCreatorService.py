from typing import List
import ast
from setup_exp.entities.Experiment import Experiment
from setup_exp.entities.FunctionGraph import FunctionGraph
from setup_exp.entities.Script import Script
from setup_exp.services.FunctionCalledDetectorService import FunctionCalledDetectorService

class ScriptFunctionGraphCreatorService(ast.NodeVisitor):
    def __init__(self, main_script:Script, dependency_scripts_names:List[str], experiment:Experiment):
        self.script_function_graph = FunctionGraph(main_script, dependency_scripts_names, experiment)

    def callback(self, data):
        if data['current_function'] is not None:
            self.script_function_graph.add(data['current_function'], data['function_called'])
