import contextlib
import io
import unittest
from unittest.mock import patch

from execute_exp.parser_params import (
    EXEC_MODES,
    EXPERIMENTAL_EXEC_MODES,
    STABLE_EXEC_MODES,
    build_parser,
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

    def test_every_option_reaches_its_position_of_the_tuple(self):
        argv = [
            "script.py",
            "program-argument",
            *("--mem-arch", "1-dict"),
            *("--retrieval-strategy", "lazy"),
            *("--retrieval-exec-mode", "thread"),
            *("-H", "md5"),
            *("-s", "redis"),
            *("--serializer", "pickle"),
            *("-mt", "2.5"),
            "--measure-time",
            "--profile",
            *("--exec-mode", "accurate"),
            *("--revalidation", "fixed"),
            *("--max-num-exec-til-revalidation", "3"),
            *("--reduction-factor", "0.5"),
            *("--min-num-exec", "7"),
            *("--min-mode-occurrence", "0.6"),
            *("--confidence-level", "0.9"),
            *("--max-error-per-function", "0.1"),
        ]
        with patch("sys.argv", argv):
            params = get_params()

        self.assertTupleEqual(
            params,
            (
                ["1-dict"],
                ["lazy"],
                ["thread"],
                ["md5"],
                ["redis"],
                ["pickle"],
                [2.5],
                True,
                True,
                ["accurate"],
                ["fixed"],
                [3],
                [0.5],
                [7],
                ["0.6"],
                ["0.9"],
                ["0.1"],
            ),
        )

    def test_the_long_names_of_the_short_options_are_accepted(self):
        argv = [
            "script.py",
            *("--hash", "a5hash"),
            *("--storage", "mongo-gridfs"),
            *("--min-exec-time-to-memoize", "0"),
        ]
        with patch("sys.argv", argv):
            params = get_params()

        self.assertEqual(params[3], ["a5hash"])
        self.assertEqual(params[4], ["mongo-gridfs"])
        self.assertEqual(params[6], [0.0])

    def test_the_hashes_are_the_public_ones_and_the_research_ones(self):
        hash_action = next(
            action for action in build_parser()._actions if action.dest == "hash"
        )

        self.assertListEqual(
            list(hash_action.choices), ["xxhash", "md5", "a5hash", "museair"]
        )
        self.assertIn(
            "Research hashes are not supported in SpeeduPy 2.0 and are evaluated "
            "in a separate issue.",
            " ".join(help_output().split()),
        )

    def test_a_value_outside_the_choices_exits_with_status_2(self):
        for option in ("-H", "-s", "--mem-arch", "--serializer", "--exec-mode"):
            err = io.StringIO()
            with (
                self.subTest(option=option),
                patch("sys.argv", ["script.py", option, "nothing"]),
                contextlib.redirect_stderr(err),
                self.assertRaises(SystemExit) as raised,
            ):
                get_params()

            self.assertEqual(raised.exception.code, 2)
            self.assertIn("invalid choice: 'nothing'", err.getvalue())

    def test_build_parser_parses_nothing(self):
        with patch("sys.argv", ["script.py", "--unknown-option"]):
            parser = build_parser()

        self.assertEqual(parser.parse_args([]).storage, ["sqlite"])


if __name__ == "__main__":
    unittest.main()
