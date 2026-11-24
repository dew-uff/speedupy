import json
import os
import unittest
from unittest.mock import patch

import speedupy
from constants import Constants
from execute_exp.parser_params import EXEC_MODES, EXPERIMENTAL_EXEC_MODES
from execute_exp.services.setup_mode import check_setup_mode
from execute_exp.SpeeduPySettings import SpeeduPySettings
from SingletonMeta import SingletonMeta


def record_setup_mode(exec_mode):
    os.makedirs(Constants().FOLDER_NAME, exist_ok=True)
    with open(Constants().EXP_SETUP_MODE_FILENAME, "w") as f:
        json.dump({"exec_mode": exec_mode}, f)


class TestSetupMode(unittest.TestCase):
    def tearDown(self):
        os.system(f"rm -rf {Constants().FOLDER_NAME}")

    def test_an_experimental_run_over_a_manual_setup_fails_with_a_clear_message(self):
        record_setup_mode("manual")

        with self.assertRaises(RuntimeError) as raised:
            check_setup_mode("accurate")

        self.assertEqual(
            str(raised.exception),
            "setup was run in manual mode, so no function is marked "
            "@maybe_deterministic; run setup again with --exec-mode accurate",
        )

    def test_an_experimental_run_over_a_no_cache_setup_fails(self):
        record_setup_mode("no-cache")

        for exec_mode in EXPERIMENTAL_EXEC_MODES:
            with self.subTest(exec_mode=exec_mode):
                with self.assertRaises(RuntimeError) as raised:
                    check_setup_mode(exec_mode)
                self.assertIn("setup was run in no-cache mode", str(raised.exception))
                self.assertIn(f"--exec-mode {exec_mode}", str(raised.exception))

    def test_an_experimental_run_over_an_experimental_setup_proceeds(self):
        for setup_mode in EXPERIMENTAL_EXEC_MODES:
            record_setup_mode(setup_mode)
            for exec_mode in EXPERIMENTAL_EXEC_MODES:
                with self.subTest(setup_mode=setup_mode, exec_mode=exec_mode):
                    check_setup_mode(exec_mode)

    def test_an_experimental_run_without_a_setup_record_proceeds(self):
        check_setup_mode("accurate")

    def test_an_experimental_run_with_an_unreadable_record_proceeds(self):
        os.makedirs(Constants().FOLDER_NAME, exist_ok=True)
        with open(Constants().EXP_SETUP_MODE_FILENAME, "w") as f:
            f.write("not json")

        check_setup_mode("accurate")

    def test_manual_and_no_cache_runs_touch_no_file(self):
        record_setup_mode("manual")

        with (
            patch("execute_exp.services.setup_mode.os.path.exists") as exists,
            patch("builtins.open") as opened,
        ):
            for exec_mode in ("manual", "no-cache"):
                with self.subTest(exec_mode=exec_mode):
                    check_setup_mode(exec_mode)

        exists.assert_not_called()
        opened.assert_not_called()

    def test_every_execution_mode_is_either_stable_or_experimental(self):
        self.assertSetEqual(
            set(EXEC_MODES), {"no-cache", "manual", *EXPERIMENTAL_EXEC_MODES}
        )

    def test_speedupy_checks_the_setup_mode_before_anything_else(self):
        record_setup_mode("manual")
        saved = dict(vars(SpeeduPySettings()))
        self.addCleanup(vars(SpeeduPySettings()).update, saved)
        SpeeduPySettings().exec_mode = ["accurate"]
        SingletonMeta._instances.pop(speedupy.SpeeduPy, None)

        with self.assertRaises(RuntimeError) as raised:
            speedupy.SpeeduPy()

        self.assertIn("setup was run in manual mode", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
