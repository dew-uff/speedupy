import json
import os
import sys
import unittest
import unittest.mock
from hashlib import md5

from remove_paths import remove_paths
from xxhash import xxh64_intdigest, xxh128_hexdigest

from util import check_python_version, save_json_file


class TestUtil(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.JSON_FILENAME = "test.json"

    def setUp(self):
        # The tests assign to sys.version_info; patch.object puts it back.
        patcher = unittest.mock.patch.object(sys, "version_info", sys.version_info)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_check_python_version_with_minimum_version(self):
        sys.version_info = (3, 11, 0)
        check_python_version()

    def test_check_python_version_with_later_patch_of_supported_version(self):
        sys.version_info = (3, 11, 99)
        check_python_version()

    def test_check_python_version_with_last_version_below_the_range(self):
        sys.version_info = (3, 10, 99)
        self.assertRaises(Exception, check_python_version)

    def test_check_python_version_with_highest_supported_version(self):
        sys.version_info = (3, 15, 99)
        check_python_version()

    def test_check_python_version_with_first_version_above_the_range(self):
        sys.version_info = (3, 16, 0)
        self.assertRaisesRegex(
            Exception, r"Requires Python 3\.11 to 3\.15", check_python_version
        )

    def test_check_python_version_with_incorrect_version_greater_than_minimum(self):
        sys.version_info = (4, 1)
        self.assertRaises(Exception, check_python_version)

    def test_check_python_version_with_incorrect_version_lower_than_minimum(self):
        sys.version_info = (2, 7)
        self.assertRaises(Exception, check_python_version)

    def test_save_json_file(self):
        self.assertFalse(os.path.exists(self.JSON_FILENAME))
        data = {
            "f1": md5("def f1():\n\treturn 'f1'".encode("utf")).hexdigest(),
            "f2": xxh64_intdigest(
                "def f2(a, b, c=3):\n\treturn a ** b + c".encode("utf")
            ),
            "f3": xxh128_hexdigest("def f3(x, y):\n\treturn x/y".encode("utf")),
        }
        save_json_file(data, self.JSON_FILENAME)
        self.assertTrue(os.path.exists(self.JSON_FILENAME))
        with open(self.JSON_FILENAME) as f:
            data2 = json.load(f)
        self.assertDictEqual(data, data2)
        remove_paths(self.JSON_FILENAME)


if __name__ == "__main__":
    unittest.main()
