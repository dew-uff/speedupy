import ast

from setup_exp.entities.Experiment import Experiment
from setup_exp.entities.FunctionGraph import FunctionGraph
from setup_exp.entities.Script import Script
from setup_exp.services.FunctionCalledDetectorService import (
    FunctionCalledDetectorService,
)
from setup_exp.services.PubSub import PubSub


class ScriptFunctionCallHierarchyAnalyzer(ast.NodeVisitor, PubSub):
    def __init__(self, main_script: Script, experiment: Experiment):
        super().__init__()
        self.__experiment = experiment
        self.__script = main_script
        self.__function_call_detector = FunctionCalledDetectorService(
            self.__script, self.__experiment
        )

    def analyze(self) -> FunctionGraph:
        self.__current_function_name = ""
        self.__current_function = None
        self.visit(self.__script.AST)

    def visit_ClassDef(self, node):
        """This function avoids that child nodes of a ClassDef node
        (ex.: class methods) be visited during search"""

    def visit_FunctionDef(self, node):
        previous_function_name = self.__current_function_name
        self.__current_function_name = (
            node.name
            if self.__current_function_name == ""
            else self.__current_function_name + ".<locals>." + node.name
        )
        previous_function = self.__current_function
        self.__current_function = node

        self.publish("function_def", node)

        self.generic_visit(node)

        self.__current_function_name = previous_function_name
        self.__current_function = previous_function

    def visit_Call(self, node):
        function_called = None

        if isinstance(node.func, ast.Name):
            # In this case the function called can be either a function imported
            # with the command "from ... import ..." or a function declared by the
            # user in the file

            function_called_name = node.func.id
            function_called = self.__function_call_detector.find_function_called(
                function_called_name
            )

        elif isinstance(node.func, ast.Attribute):
            # In this case the function called is a function imported with the command
            # "import ..."

            # Building the name of the function called
            current_node = node.func
            function_called_name_parts = []
            while isinstance(current_node, ast.Attribute):
                function_called_name_parts.append(current_node.attr)
                current_node = current_node.value
            if not isinstance(current_node, ast.Name):
                # The receiver is a subscript, a call, a literal...: the call
                # cannot be a function of the experiment. Calls nested in the
                # receiver are still visited.
                self.generic_visit(node)
                return
            function_called_name_parts.append(current_node.id)

            function_called_name_parts.reverse()
            function_called_name = ".".join(function_called_name_parts)

            function_called = self.__function_call_detector.find_function_called(
                function_called_name
            )

        if function_called is not None:
            self.publish(
                "function_call",
                {
                    "current_function": self.__current_function,
                    "function_called": function_called,
                    "function_call": node,
                },
            )

        self.generic_visit(node)
