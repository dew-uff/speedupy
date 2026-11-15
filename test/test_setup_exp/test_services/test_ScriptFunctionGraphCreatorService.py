import unittest, os, sys, ast
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split("test/")[0]
sys.path.append(project_folder)

from setup_exp.entities.Script import Script
from setup_exp.entities.Experiment import Experiment
from setup_exp.services.ScriptFunctionGraphCreatorService import (
    ScriptFunctionGraphCreatorService,
)
from setup_exp.services.ScriptFunctionCallHierarchyAnalyzer import (
    ScriptFunctionCallHierarchyAnalyzer,
)
from setup_exp.entities.FunctionGraph import FunctionGraph


class TestScriptFunctionGraphCreatorService(unittest.TestCase):
    def setUp(self):
        self.define_ast_nodes()

        self.script = Script(functions={"f1": self.f1, "f2": self.f2})
        self.dependency_scripts_names = []
        self.experiment = Experiment("folder/")
        self.analyzer = Mock(ScriptFunctionCallHierarchyAnalyzer)
        self.function_graph_creator = ScriptFunctionGraphCreatorService(
            self.script, self.dependency_scripts_names, self.experiment, self.analyzer
        )

    def define_ast_nodes(self):
        self.f1 = ast.FunctionDef(
            name="f1",
            args=ast.arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[ast.Return(value=ast.Constant(value=1))],
            decorator_list=[],
        )

        self.f2 = ast.FunctionDef(
            name="f2",
            args=ast.arguments(
                posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
            ),
            body=[ast.Return(value=ast.Constant(value="hello"))],
            decorator_list=[],
        )

        self.call = ast.Call(
            func=ast.Name(id="f2", ctx=ast.Load()), args=[], keywords=[]
        )

    def test_constructor(self):
        self.analyzer.subscribe.assert_called_once_with(
            "function_call", self.function_graph_creator.callback
        )
        self.assertIsInstance(
            self.function_graph_creator.script_function_graph, FunctionGraph
        )
        self.assertDictEqual(
            self.function_graph_creator.script_function_graph.graph,
            {self.f1: [], self.f2: []},
        )

    def test_callback_when_function_called_from_global_scope(self):
        data = {
            "current_function": None,
            "function_called": self.f2,
            "function_call": self.call,
        }
        self.function_graph_creator.callback(data)
        self.assertDictEqual(
            self.function_graph_creator.script_function_graph.graph,
            {self.f1: [], self.f2: []},
        )

    def test_callback_when_a_function_called_another_function(self):
        data = {
            "current_function": self.f1,
            "function_called": self.f2,
            "function_call": self.call,
        }
        self.function_graph_creator.callback(data)
        self.assertDictEqual(
            self.function_graph_creator.script_function_graph.graph,
            {self.f1: [self.f2], self.f2: []},
        )


if __name__ == "__main__":
    unittest.main()
