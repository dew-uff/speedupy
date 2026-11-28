"""check-pins.py compares requirements.txt with [project.dependencies].

A package may have one pin per environment marker (issue #164), and every pin
is compared, not only the last one of each name.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "check-pins.py"

OLD = "numpy==2.4.6; python_version < '3.15'"
NEW = "numpy==2.5.5; python_version >= '3.15'"


class TestCheckPins(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)

    def check(self, requirements, dependencies):
        req = self.directory / "requirements.txt"
        req.write_text("".join(f"{line}\n" for line in requirements))
        pyproject = self.directory / "pyproject.toml"
        items = "".join(f'    "{line}",\n' for line in dependencies)
        pyproject.write_text(f"[project]\ndependencies = [\n{items}]\n")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(req), str(pyproject)],
            capture_output=True,
            text=True,
            check=False,
        )

    def assert_differ(self, result, expected):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected, result.stderr)

    def test_equal_pins_agree(self):
        result = self.check(["xxhash==4.1.0"], ["xxhash==4.1.0"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ok: 1 pins agree", result.stdout)

    def test_different_pins_are_reported(self):
        result = self.check(["xxhash==4.1.0"], ["xxhash==4.0.0"])

        self.assert_differ(result, "xxhash")

    def test_a_pin_only_in_one_file_is_reported(self):
        result = self.check(["xxhash==4.1.0", "redis==8.1.0"], ["xxhash==4.1.0"])

        self.assert_differ(result, "redis: only in")

    def test_two_pins_of_one_package_with_different_markers_agree(self):
        result = self.check([OLD, NEW], [OLD, NEW])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ok: 2 pins agree", result.stdout)

    def test_the_first_of_two_pins_of_one_package_is_compared(self):
        changed = OLD.replace("2.4.6", "2.4.5")

        result = self.check([changed, NEW], [OLD, NEW])

        self.assert_differ(result, "2.4.5")

    def test_a_missing_pin_of_one_marker_is_reported(self):
        result = self.check([NEW], [OLD, NEW])

        self.assert_differ(result, "python_version<")

    def test_different_markers_are_reported(self):
        changed = NEW.replace("3.15", "3.14")

        result = self.check([OLD, changed], [OLD, NEW])

        self.assert_differ(result, "3.14")

    def test_the_spacing_and_the_quotes_of_a_marker_do_not_matter(self):
        spaced = 'numpy==2.4.6 ;python_version<"3.15"'

        result = self.check([spaced], [OLD])

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
