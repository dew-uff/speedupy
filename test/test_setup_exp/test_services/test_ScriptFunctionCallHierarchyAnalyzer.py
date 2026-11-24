import os
import unittest

from setup_exp.services.experiment_service import create_experiment
from setup_exp.services.ScriptFunctionCallHierarchyAnalyzer import (
    ScriptFunctionCallHierarchyAnalyzer,
)


class TestScriptFunctionCallHierarchyAnalyzer(unittest.TestCase):
    # The tests write in the current directory, which is the scratch directory of
    # the session (see test/conftest.py), never the directory of this file.
    SCRIPT = "script_test.py"
    OTHER = "script_test_2.py"

    def tearDown(self):
        for f in [self.SCRIPT, self.OTHER]:
            if os.path.exists(f):
                os.remove(f)

    def analyze(self, code: str, other: str = None) -> list:
        """Analyzes the script and returns the names of the functions called that
        the analyzer published as functions of the experiment."""
        with open(self.SCRIPT, "wt") as f:
            f.write(code)
        if other is not None:
            with open(self.OTHER, "wt") as f:
                f.write(other)
        experiment = create_experiment(os.path.join(os.getcwd(), self.SCRIPT))
        analyzer = ScriptFunctionCallHierarchyAnalyzer(
            experiment.main_script, experiment
        )
        published = []
        analyzer.subscribe(
            "function_call", lambda data: published.append(data["function_called"].name)
        )
        analyzer.analyze()
        return published

    def test_a_call_on_a_subscript_is_skipped(self):
        published = self.analyze(
            "def total(table, key):\n    return table[key].sum()\n"
        )

        self.assertEqual(published, [])

    def test_a_call_on_the_result_of_a_call_is_skipped(self):
        published = self.analyze("def total(f):\n    return f().g()\n")

        self.assertEqual(published, [])

    def test_a_call_on_a_literal_is_skipped(self):
        published = self.analyze("def join(parts):\n    return 'x'.join(parts)\n")

        self.assertEqual(published, [])

    def test_a_call_nested_in_a_call_receiver_is_still_detected(self):
        published = self.analyze(
            "def helper():\n    return 1\n\n\ndef total():\n    return helper().g()\n"
        )

        self.assertEqual(published, ["helper"])

    def test_a_call_nested_in_the_arguments_of_a_subscript_call_is_still_detected(
        self,
    ):
        published = self.analyze(
            "def helper(x):\n    return x\n\n\n"
            "def total(table, key):\n    return table[key].sum(helper(1))\n"
        )

        self.assertEqual(published, ["helper"])

    def test_a_call_on_an_imported_module_still_resolves(self):
        published = self.analyze(
            "import script_test_2\n\n\n"
            "def total():\n    return script_test_2.function()\n",
            other="def function():\n    return 1\n",
        )

        self.assertEqual(published, ["function"])

    def test_a_direct_call_by_name_still_resolves(self):
        published = self.analyze(
            "def helper():\n    return 1\n\n\ndef total():\n    return helper()\n"
        )

        self.assertEqual(published, ["helper"])
