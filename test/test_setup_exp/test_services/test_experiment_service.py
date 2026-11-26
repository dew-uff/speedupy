import ast
import hashlib
import os
import unittest
import unittest.mock

from execute_exp.parser_params import EXPERIMENTAL_EXEC_MODES
from setup_exp.services.experiment_service import (
    create_experiment,
    decorate_experiment_functions,
    get_experiment_functions_hashes,
)


class TestExperimentService(unittest.TestCase):
    def tearDown(self):
        files_and_folders = [
            "script_test.py",
            "script_test_2.py",
            "script_test_3.py",
            "folder",
            "folder2",
            "folder3",
            "folder4",
        ]
        for f in files_and_folders:
            if os.path.exists(f):
                os.system(f"rm -rf {f}")
                # pass

    def getAST(self, script_name: str) -> ast.Module:
        with open(script_name, "rt") as f:
            fileAST = ast.parse(f.read())
        return fileAST

    def normalize_string(self, string):
        return string.replace("\n\n", "\n").replace("\t", "    ").replace('"', "'")

    def write_experiment(self):
        with open("script_test_2.py", "w") as f:
            f.write("def helper(x):\n    return x + 1\n")
        with open("script_test.py", "w") as f:
            f.write(
                "import script_test_2\n\n\n"
                "def add(a, b):\n    return a + b\n\n\n"
                "def main():\n    print(add(1, 2), script_test_2.helper(1))\n"
            )
        return create_experiment("script_test.py")

    def unparse(self, experiment, script_name):
        return ast.unparse(experiment.scripts[script_name].AST)

    def test_decorate_experiment_functions_in_experimental_modes_injects_maybe_deterministic(
        self,
    ):
        for exec_mode in EXPERIMENTAL_EXEC_MODES:
            with self.subTest(exec_mode=exec_mode):
                experiment = self.write_experiment()

                decorate_experiment_functions(experiment, exec_mode=exec_mode)

                main_code = self.unparse(experiment, "script_test.py")
                self.assertIn("@maybe_deterministic\ndef add", main_code)
                # decorate_function skips a function that already carries a
                # SpeeduPy decorator: `main` gets @initialize_speedupy only.
                self.assertIn("@initialize_speedupy\ndef main", main_code)
                self.assertNotIn(
                    "@initialize_speedupy\n@maybe_deterministic", main_code
                )
                self.assertIn(
                    "from speedupy.speedupy import maybe_deterministic", main_code
                )
                self.assertIn(
                    "@maybe_deterministic\ndef helper",
                    self.unparse(experiment, "script_test_2.py"),
                )

    def test_decorate_experiment_functions_in_manual_mode_injects_only_initialize_speedupy(
        self,
    ):
        experiment = self.write_experiment()

        decorate_experiment_functions(experiment, exec_mode="manual")

        main_code = self.unparse(experiment, "script_test.py")
        self.assertNotIn("maybe_deterministic", main_code)
        self.assertIn("@initialize_speedupy\ndef main", main_code)
        self.assertIn("from speedupy.speedupy import initialize_speedupy", main_code)

    def test_decorate_experiment_functions_in_no_cache_mode_injects_only_initialize_speedupy(
        self,
    ):
        experiment = self.write_experiment()

        decorate_experiment_functions(experiment, exec_mode="no-cache")

        main_code = self.unparse(experiment, "script_test.py")
        self.assertNotIn("maybe_deterministic", main_code)
        self.assertIn("@initialize_speedupy\ndef main", main_code)

    def test_decorate_experiment_functions_without_maybe_deterministic_leaves_other_scripts_untouched(
        self,
    ):
        experiment = self.write_experiment()

        decorate_experiment_functions(experiment, exec_mode="manual")

        self.assertEqual(
            self.unparse(experiment, "script_test_2.py"),
            "def helper(x):\n    return x + 1",
        )

    def test_get_experiment_functions_hashes_declares_md5_as_not_used_for_security(
        self,
    ):
        # A FIPS-mode OpenSSL refuses md5 unless the caller says that the digest
        # is not a security one.
        real_md5 = hashlib.md5

        def fips_md5(data=b"", *, usedforsecurity=True):
            if usedforsecurity:
                raise ValueError("md5 is disabled for security use")
            return real_md5(data, usedforsecurity=False)

        function = unittest.mock.Mock(qualname="f")
        function_graph = unittest.mock.Mock(graph={function: []})
        function_graph.get_source_code_executed.return_value = "def f():\n    return 1"

        with unittest.mock.patch("hashlib.md5", fips_md5):
            result = get_experiment_functions_hashes(function_graph)

        self.assertEqual(result, {"f": "26a04d101487fb4ca1ec5ba96baf63eb"})


if __name__ == "__main__":
    unittest.main()
