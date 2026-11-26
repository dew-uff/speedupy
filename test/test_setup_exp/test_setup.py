import ast
import json
import os
import socket
import sys
import unittest
from unittest.mock import patch

from remove_paths import remove_paths

import setup_exp.setup as setup
from execute_exp.parser_params import (
    EXEC_MODES,
    EXPERIMENTAL_EXEC_MODES,
    STORAGE_OPTIONS,
)


class TestSetup(unittest.TestCase):
    def setUp(self):
        # The tests assign to sys.argv; patch.object puts it back.
        patcher = patch.object(sys, "argv", sys.argv)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        paths = [".speedupy/", "teste.xyz", "teste.temp", "folder1", "folder2"]
        remove_paths(*paths)

    def test_validate_main_script_specified_when_no_script_was_specified(self):
        sys.argv = ["setup.py"]
        self.assertRaises(Exception, setup.validate_main_script_specified)

    def test_validate_main_script_specified_when_main_script_was_specified(self):
        sys.argv = ["setup.py", "main_script.py"]
        setup.validate_main_script_specified()

    def test_validate_main_script_specified_when_many_scripts_were_specified(self):
        sys.argv = ["setup.py", "script1.py", "script2.py"]
        self.assertRaises(Exception, setup.validate_main_script_specified)

    def test_validate_main_script_specified_with_a_storage_and_one_script(self):
        sys.argv = ["setup.py", "-s", "redis", "main_script.py"]
        setup.validate_main_script_specified()

    def test_validate_main_script_specified_with_a_storage_and_no_script(self):
        sys.argv = ["setup.py", "-s", "redis"]
        self.assertRaises(Exception, setup.validate_main_script_specified)

    def test_parse_args_defaults_to_the_file_storage(self):
        args = setup.parse_args(["main_script.py"])
        self.assertEqual(args.storage, "file")
        self.assertListEqual(args.main_script, ["main_script.py"])

    def test_parse_args_accepts_every_storage_of_the_execution(self):
        for storage in STORAGE_OPTIONS:
            for flag in ("-s", "--storage"):
                with self.subTest(storage=storage, flag=flag):
                    args = setup.parse_args([flag, storage, "main_script.py"])
                    self.assertEqual(args.storage, storage)
                    self.assertListEqual(args.main_script, ["main_script.py"])

    def test_parse_args_accepts_the_storage_after_the_script(self):
        args = setup.parse_args(["main_script.py", "-s", "mysql"])
        self.assertEqual(args.storage, "mysql")

    def test_parse_args_rejects_an_unknown_storage(self):
        with self.assertRaises(SystemExit) as raised:
            setup.parse_args(["-s", "oracle", "main_script.py"])
        self.assertEqual(raised.exception.code, 2)

    def test_parse_args_defaults_to_the_manual_exec_mode(self):
        self.assertEqual(setup.parse_args(["main_script.py"]).exec_mode, "manual")

    def test_parse_args_accepts_every_exec_mode_of_the_execution(self):
        self.assertListEqual(
            EXEC_MODES,
            [
                "no-cache",
                "manual",
                "accurate",
                "probabilistic-counting",
                "probabilistic-error",
            ],
        )
        for exec_mode in EXEC_MODES:
            with self.subTest(exec_mode=exec_mode):
                args = setup.parse_args(["--exec-mode", exec_mode, "main_script.py"])
                self.assertEqual(args.exec_mode, exec_mode)
                self.assertListEqual(args.main_script, ["main_script.py"])

    def test_parse_args_rejects_an_unknown_exec_mode(self):
        with self.assertRaises(SystemExit) as raised:
            setup.parse_args(["--exec-mode", "turbo", "main_script.py"])
        self.assertEqual(raised.exception.code, 2)

    def test_the_storage_names_are_the_executions(self):
        self.assertListEqual(
            sorted(STORAGE_OPTIONS),
            sorted(
                [
                    "sqlite",
                    "redis",
                    "mongo",
                    "gridfs",
                    "mongo-file",
                    "mongo-gridfs",
                    "file",
                    "mysql",
                ]
            ),
        )


class TestSetupWithoutServers(unittest.TestCase):
    """Setting up an experiment reaches no server unless its storage is one."""

    SCRIPT = "script_test_no_servers.py"

    def setUp_script(self):
        with open(self.SCRIPT, "w") as f:
            f.write(
                "def add(a, b):\n    return a + b\n\n\n"
                "def main():\n    print(add(1, 2))\n\n\n"
                'if __name__ == "__main__":\n    main()\n'
            )

    def setUp(self):
        self.setUp_script()
        # Any attempt to open a connection fails: no server is reachable, and
        # none is touched when one happens to be running.
        patcher = patch.object(
            socket.socket,
            "connect",
            side_effect=ConnectionRefusedError("no server in this test"),
        )
        self.connect = patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        remove_paths(".speedupy/", self.SCRIPT)

    def test_setup_experiment_with_the_default_storage_reaches_no_server(self):
        setup.setup_experiment(self.SCRIPT)

        self.connect.assert_not_called()
        self.assertTrue(os.path.isdir(".speedupy/cache"))

    def test_setup_experiment_with_the_sqlite_storage_reaches_no_server(self):
        setup.setup_experiment(self.SCRIPT, "sqlite")

        self.connect.assert_not_called()
        self.assertTrue(os.path.isfile(".speedupy/speedupy.db"))

    def rewritten_script(self):
        with open(self.SCRIPT) as f:
            return f.read()

    def test_setup_experiment_in_the_default_mode_decorates_main_and_nothing_else(
        self,
    ):
        setup.setup_experiment(self.SCRIPT)

        code = self.rewritten_script()
        self.assertNotIn("maybe_deterministic", code)
        self.assertIn("@initialize_speedupy\ndef main", code)
        self.assertEqual(
            code.count("from speedupy.speedupy import"), 1, "only initialize_speedupy"
        )
        self.assertTrue(os.path.isfile(".speedupy/functions_speedupy.json"))

    def test_setup_experiment_in_the_default_mode_matches_the_manual_mode(self):
        setup.setup_experiment(self.SCRIPT)
        default_code = self.rewritten_script()
        remove_paths(".speedupy", self.SCRIPT)
        self.setUp_script()

        setup.setup_experiment(self.SCRIPT, exec_mode="manual")

        self.assertEqual(self.rewritten_script(), default_code)

    def test_setup_experiment_in_an_experimental_mode_injects_maybe_deterministic(
        self,
    ):
        for exec_mode in EXPERIMENTAL_EXEC_MODES:
            with self.subTest(exec_mode=exec_mode):
                remove_paths(".speedupy", self.SCRIPT)
                self.setUp_script()

                setup.setup_experiment(self.SCRIPT, exec_mode=exec_mode)

                code = self.rewritten_script()
                self.assertIn("@maybe_deterministic\ndef add", code)
                self.assertIn("from speedupy.speedupy import maybe_deterministic", code)
                self.assertIn("@initialize_speedupy\ndef main", code)

    def test_setup_experiment_in_the_no_cache_mode_injects_no_maybe_deterministic(
        self,
    ):
        setup.setup_experiment(self.SCRIPT, exec_mode="no-cache")

        self.assertNotIn("maybe_deterministic", self.rewritten_script())
        self.assertTrue(os.path.isfile(".speedupy/functions_speedupy.json"))

    def test_setup_experiment_with_a_call_on_a_subscript(self):
        with open(self.SCRIPT, "w") as f:
            f.write(
                "from speedupy.speedupy import deterministic\n\n\n"
                "@deterministic\ndef total(table, key):\n    return table[key].sum()\n\n\n"
                'def main():\n    print(total({"a": [1, 2, 3]}, "a"))\n\n\n'
                'if __name__ == "__main__":\n    main()\n'
            )

        setup.setup_experiment(self.SCRIPT)

        code = self.rewritten_script()
        ast.parse(code)
        self.assertIn("@deterministic\ndef total", code)
        self.assertIn("@initialize_speedupy\ndef main", code)

    def test_setup_experiment_records_its_exec_mode(self):
        for exec_mode in EXEC_MODES:
            with self.subTest(exec_mode=exec_mode):
                remove_paths(".speedupy", self.SCRIPT)
                self.setUp_script()

                setup.setup_experiment(self.SCRIPT, exec_mode=exec_mode)

                with open(".speedupy/setup_mode.json") as f:
                    self.assertDictEqual(json.load(f), {"exec_mode": exec_mode})
