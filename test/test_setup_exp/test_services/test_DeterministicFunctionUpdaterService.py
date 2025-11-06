import unittest, os, sys, ast
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from setup_exp.services.DeterministicFunctionUpdaterService import DeterministicFunctionUpdaterService
from setup_exp.services.ScriptFunctionCallHierarchyAnalyzer import ScriptFunctionCallHierarchyAnalyzer


class TestDeterministicFunctionUpdaterService(unittest.TestCase):
    def setUp(self):
        self.analyzer = Mock(ScriptFunctionCallHierarchyAnalyzer)
        self.det_function_updater_service = DeterministicFunctionUpdaterService(self.analyzer)

    def test_constructor_subscription(self):
        self.analyzer.subscribe.assert_any_call('function_def', self.det_function_updater_service.update_determinsitic_function_def)
        self.analyzer.subscribe.assert_any_call('function_call', self.det_function_updater_service.update_deterministic_function_call)
        self.assertEqual(self.analyzer.subscribe.call_count, 2)

    def test_update_determinsitic_function_def_when_function_is_not_marked_with_deterministic_decorator(self):
        code = "def f(a, b, c=1, d=2):\n\treturn 15"
        node = ast.parse(code).body[0]
        self.det_function_updater_service.update_determinsitic_function_def(node)
        self.assertListEqual(['a', 'b', 'c', 'd'], [a.arg for a in node.args.args])
        self.assertListEqual([1, 2], [c.value for c in node.args.defaults])

    def test_update_determinsitic_function_def_when_function_is_marked_with_deterministic_decorator_and_already_has_func_globals_kwarg(self):
        code = "@deterministic\ndef f(a, b, func_globals=None, c=1, d=2):\n\treturn 15"
        node = ast.parse(code).body[0]
        self.det_function_updater_service.update_determinsitic_function_def(node)
        self.assertListEqual(['a', 'b', 'func_globals', 'c', 'd'], [a.arg for a in node.args.args])
        self.assertListEqual([None, 1, 2], [c.value for c in node.args.defaults])

    def test_update_determinsitic_function_def_when_function_is_marked_with_deterministic_decorator_and_does_not_have_func_globals_kwarg(self):
        code = "@deterministic\ndef f(a, b, c=1, d=2):\n\treturn 15"
        node = ast.parse(code).body[0]
        self.det_function_updater_service.update_determinsitic_function_def(node)
        self.assertListEqual(['a', 'b', 'c', 'd', 'func_globals'], [a.arg for a in node.args.args])
        self.assertListEqual([1, 2, None], [c.value for c in node.args.defaults])

    def test_update_deterministic_function_call_when_function_is_not_marked_with_deterministic_decorator(self): pass

    def test_update_deterministic_function_call_when_function_is_marked_with_deterministic_decorator_and_the_call_already_has_func_globals_kwarg(self): pass
    def test_update_deterministic_function_call_when_function_is_marked_with_deterministic_decorator_and_the_call_does_not_have_func_globals_kwarg(self): pass


if __name__ == '__main__':
    unittest.main()
