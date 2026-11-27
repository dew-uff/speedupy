"""The option table of the README is held to the parser, in both directions.

The table under "Execution Options" has one row per option: the short name, the
long name, a description and the accepted values. Every name and every value is
written between backticks; a cell of "Accepted Values" with no backticks is an
option that takes none, or a free one.

The options of the parser group "Experimental options (beta)" stay out of the
README (decision D8): docs/experimental.md lists them, and is held to the group.
"""

import argparse
import re
import unittest
from pathlib import Path

from execute_exp.parser_params import build_parser

CHECKOUT = Path(__file__).resolve().parents[1]
README = CHECKOUT / "README.md"
EXPERIMENTAL_DOC = CHECKOUT / "docs" / "experimental.md"

SECTION = "### Execution Options"
HEADER = ["Short Arg", "Long Arg", "Description", "Accepted Values"]
EXPERIMENTAL_GROUP = "Experimental options (beta)"

_CODE = re.compile(r"`([^`]+)`")


def readme_options(text: str) -> list:
    """The rows of the option table, as (names, values) pairs of sets."""
    lines = text.splitlines()
    if SECTION not in lines:
        raise AssertionError(f"README.md has no '{SECTION}' section")

    table = []
    for line in lines[lines.index(SECTION) + 1 :]:
        if line.startswith("#"):
            break
        if line.startswith("|"):
            table.append([cell.strip() for cell in line.strip().strip("|").split("|")])

    if not table or table[0] != HEADER:
        raise AssertionError(f"'{SECTION}' needs a table with the columns {HEADER}")

    rows = []
    # table[1] is the line that aligns the columns.
    for cells in table[2:]:
        if len(cells) != len(HEADER):
            raise AssertionError(f"row with {len(cells)} cells: {cells}")
        short, long, _, values = cells
        names = set(_CODE.findall(short) + _CODE.findall(long))
        if not names:
            raise AssertionError(f"row that names no option: {cells}")
        rows.append((names, set(_CODE.findall(values))))
    if not rows:
        raise AssertionError(f"the table of '{SECTION}' has no rows")
    return rows


def experimental_actions(parser) -> list:
    groups = [g for g in parser._action_groups if g.title == EXPERIMENTAL_GROUP]
    if len(groups) != 1:
        raise AssertionError(f"the parser has no group '{EXPERIMENTAL_GROUP}'")
    return groups[0]._group_actions


def differences(text: str, parser) -> list:
    """One message for each option or value that only one of the two sides has."""
    experimental = experimental_actions(parser)
    options = [action for action in parser._actions if action.option_strings]
    by_name = {name: action for action in options for name in action.option_strings}

    found = []
    documented = []
    for names, values in readme_options(text):
        label = "/".join(sorted(names))
        unknown = sorted(names - by_name.keys())
        found += [f"{name}: in the README, not in the parser" for name in unknown]
        actions = {by_name[name] for name in names if name in by_name}
        if not actions:
            continue
        if len(actions) > 1:
            found.append(f"{label}: one row of the README names several options")
            continue

        action = actions.pop()
        if action in documented:
            found.append(f"{label}: the README has two rows for this option")
        documented.append(action)
        found += [
            f"{name}: in the parser, not in the README row of {label}"
            for name in sorted(set(action.option_strings) - names)
        ]
        choices = {str(choice) for choice in action.choices or ()}
        found += [
            f"{label}: value '{value}' is in the parser, not in the README"
            for value in sorted(choices - values)
        ]
        found += [
            f"{label}: value '{value}' is in the README, not in the parser"
            for value in sorted(values - choices)
        ]

    found += [
        f"{'/'.join(action.option_strings)}: in the parser, not in the README"
        for action in options
        if action not in documented and action not in experimental
    ]
    return found


class TestReadmeOptionTable(unittest.TestCase):
    def test_the_readme_table_matches_the_parser(self):
        found = differences(README.read_text(encoding="utf-8"), build_parser())

        self.assertListEqual(found, [], "\n" + "\n".join(found))

    def test_the_experimental_document_lists_the_experimental_options(self):
        text = EXPERIMENTAL_DOC.read_text(encoding="utf-8")
        section = text.split("\n## What they are\n")[1].split("\n## ")[0]
        listed = {name for name in _CODE.findall(section) if name.startswith("--")}
        expected = {
            name
            for action in experimental_actions(build_parser())
            for name in action.option_strings
        }

        # --help is where the section says the options are listed.
        self.assertSetEqual(listed - {"--help"}, expected)


class TestReadmeComparison(unittest.TestCase):
    """The comparison reports every kind of difference, on tables made for it."""

    ROWS = (
        "| `-h` | `--help` | Help. | |",
        "| `-H` | `--hash` | Hash. | `md5`, `xxhash` |",
        "| | `--profile` | Profile. | |",
    )

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("args", nargs="*")
        self.parser.add_argument("-H", "--hash", choices=["md5", "xxhash"])
        self.parser.add_argument("--profile", action="store_true")
        group = self.parser.add_argument_group(EXPERIMENTAL_GROUP)
        group.add_argument("--revalidation", choices=["none"])

    def compare(self, *rows) -> list:
        text = "\n".join(
            [
                SECTION,
                "",
                "| " + " | ".join(HEADER) + " |",
                "| :---: | :--- | :--- | :--- |",
                *rows,
                "",
                "### Usage Examples",
                "| `--outside-the-section` | | | |",
            ]
        )
        return differences(text, self.parser)

    def test_a_table_that_matches_has_no_difference(self):
        self.assertListEqual(self.compare(*self.ROWS), [])

    def test_a_value_missing_from_the_readme_is_named(self):
        help_row, _, profile = self.ROWS
        found = self.compare(help_row, "| `-H` | `--hash` | H. | `md5` |", profile)

        self.assertListEqual(
            found, ["--hash/-H: value 'xxhash' is in the parser, not in the README"]
        )

    def test_a_value_unknown_to_the_parser_is_named(self):
        help_row, _, profile = self.ROWS
        row = "| `-H` | `--hash` | H. | `md5`, `xxhash`, `murmurhash` |"

        self.assertListEqual(
            self.compare(help_row, row, profile),
            ["--hash/-H: value 'murmurhash' is in the README, not in the parser"],
        )

    def test_an_option_missing_from_the_readme_is_named(self):
        self.assertListEqual(
            self.compare(*self.ROWS[:2]),
            ["--profile: in the parser, not in the README"],
        )

    def test_an_option_unknown_to_the_parser_is_named(self):
        self.assertListEqual(
            self.compare(*self.ROWS, "| | `--gone` | Gone. | |"),
            ["--gone: in the README, not in the parser"],
        )

    def test_a_short_name_missing_from_a_row_is_named(self):
        help_row, _, profile = self.ROWS
        row = "| | `--hash` | H. | `md5`, `xxhash` |"

        self.assertListEqual(
            self.compare(help_row, row, profile),
            ["-H: in the parser, not in the README row of --hash"],
        )

    def test_a_row_that_names_two_options_is_reported(self):
        found = self.compare(self.ROWS[0], "| `-H` | `--profile` | Mixed. | |")

        self.assertIn(
            "--profile/-H: one row of the README names several options", found
        )

    def test_a_second_row_for_an_option_is_reported(self):
        self.assertListEqual(
            self.compare(*self.ROWS, self.ROWS[2]),
            ["--profile: the README has two rows for this option"],
        )

    def test_an_experimental_option_may_be_documented_and_is_then_compared(self):
        row = "| | `--revalidation` | R. | `fixed` |"

        self.assertListEqual(
            self.compare(*self.ROWS, row),
            [
                "--revalidation: value 'none' is in the parser, not in the README",
                "--revalidation: value 'fixed' is in the README, not in the parser",
            ],
        )

    def test_a_readme_without_the_table_fails(self):
        for text in ("# SpeeduPy\n", f"{SECTION}\n\nNo table.\n"):
            with self.subTest(text=text), self.assertRaises(AssertionError):
                differences(text, self.parser)

    def test_a_table_without_rows_fails(self):
        with self.assertRaises(AssertionError):
            self.compare()


if __name__ == "__main__":
    unittest.main()
