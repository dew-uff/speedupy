import ast

from setup_exp.services.ScriptFunctionCallHierarchyAnalyzer import (
    ScriptFunctionCallHierarchyAnalyzer,
)


class DeterministicFunctionUpdaterService:
    def __init__(self, analyzer: ScriptFunctionCallHierarchyAnalyzer):
        analyzer.subscribe("function_def", self.update_determinsitic_function_def)
        analyzer.subscribe("function_call", self.update_deterministic_function_call)

    def update_determinsitic_function_def(self, function: ast.FunctionDef):
        if self._function_decorated_with_deterministic(function):
            arg_names = [a.arg for a in function.args.args]
            kwonly_names = [a.arg for a in function.args.kwonlyargs]
            all_names = arg_names + kwonly_names
            if "func_globals" in all_names:
                return

            new_arg = ast.arg(arg="func_globals", annotation=None)
            new_default = ast.Constant(value=None)

            function.args.args.append(new_arg)
            function.args.defaults.append(new_default)

    def update_deterministic_function_call(self, data):
        if self._function_decorated_with_deterministic(data["function_called"]):
            if any(kw.arg == "func_globals" for kw in data["function_call"].keywords):
                return

            kw = ast.keyword(
                arg="func_globals",
                value=ast.Call(
                    func=ast.Name(id="globals", ctx=ast.Load()), args=[], keywords=[]
                ),
            )
            data["function_call"].keywords.append(kw)

    def _function_decorated_with_deterministic(self, function: ast.FunctionDef) -> bool:
        for decorator in function.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "deterministic":
                return True
        return False
