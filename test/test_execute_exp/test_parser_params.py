import contextlib
import io
import unittest
from unittest.mock import patch

from execute_exp.parser_params import (
    EXEC_MODES,
    EXPERIMENTAL_EXEC_MODES,
    STABLE_EXEC_MODES,
    get_params,
)

EXPERIMENTAL_OPTIONS = (
    "--revalidation",
    "--max-num-exec-til-revalidation",
    "--reduction-factor",
    "--min-num-exec",
    "--min-mode-occurrence",
    "--confidence-level",
    "--max-error-per-function",
)
GROUP_TITLE = "Experimental options (beta):"


def help_output() -> str:
    out = io.StringIO()
    with patch("sys.argv", ["script.py", "--help"]), contextlib.redirect_stdout(out):
        with contextlib.suppress(SystemExit):
            get_params()
    return out.getvalue()


class TestParserParams(unittest.TestCase):
    def test_the_five_execution_modes_are_still_accepted(self):
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
        self.assertListEqual(STABLE_EXEC_MODES, ["no-cache", "manual"])
        self.assertListEqual(
            EXPERIMENTAL_EXEC_MODES,
            ["accurate", "probabilistic-counting", "probabilistic-error"],
        )
        for exec_mode in EXEC_MODES:
            with patch("sys.argv", ["script.py", "--exec-mode", exec_mode]):
                self.assertEqual(get_params()[9], [exec_mode])

    def test_help_lists_the_seven_experimental_options_in_their_own_group(self):
        text = help_output()

        self.assertIn(GROUP_TITLE, text)
        before, group = text.split(GROUP_TITLE)
        for option in EXPERIMENTAL_OPTIONS:
            with self.subTest(option=option):
                self.assertIn(f"  {option} ", group)
                self.assertNotIn(f"  {option} ", before)
        flat = " ".join(group.split())
        self.assertIn("Research in progress, not recommended", flat)
        self.assertIn("differ from the uncached run", flat)

    def test_help_keeps_the_stable_options_outside_the_experimental_group(self):
        group = help_output().split(GROUP_TITLE)[1]

        for option in ("--exec-mode", "--storage", "--hash", "--profile"):
            with self.subTest(option=option):
                self.assertNotIn(f"\n  {option} ", group)
                self.assertNotIn(f", {option} ", group)

    def test_the_defaults_did_not_change(self):
        with patch("sys.argv", ["script.py"]):
            params = get_params()

        self.assertTupleEqual(
            params,
            (
                ["2-dict-fast"],
                ["eager"],
                ["sequential"],
                ["xxhash"],
                ["sqlite"],
                ["cloudpickle"],
                [0.01],
                False,
                False,
                ["manual"],
                ["adaptative"],
                10,
                0.3,
                20,
                0.8,
                0.95,
                None,
            ),
        )


if __name__ == "__main__":
    unittest.main()
