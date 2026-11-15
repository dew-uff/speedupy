import os
import sys
import unittest

import numpy as np

project_folder = os.path.realpath(__file__).split("test/")[0]
sys.path.append(project_folder)

from execute_exp.services.serializers.util import to_canonical


class TestUtil(unittest.TestCase):
    def test_to_canonical_for_function_with_globals_file_atribute(self):
        g = {"__file__": "somefile.py", "x": 42}

        def f():
            return g["x"]

        f.__globals__.update(g)

        cleaned = to_canonical(f)
        self.assertEqual(
            cleaned, {"__function__": "f", "code": "8800640119005300", "defaults": None}
        )

    def test_to_canonical_for_function_without_globals_file_atribute(self):
        g = {"y": 100}
        code = "def f(): return y"
        exec(code, g)
        f = g["f"]
        cleaned = to_canonical(f)
        self.assertEqual(
            cleaned, {"__function__": "f", "code": "74005300", "defaults": None}
        )

    def test_to_canonical_for_numpy_ndarray(self):
        arr = np.array([1, 2, 3])
        cleaned = to_canonical(arr)
        self.assertEqual(
            cleaned, {"__ndarray__": [1, 2, 3], "dtype": "int64", "shape": (3,)}
        )

    def test_to_canonical_for_numpy_generic(self):
        val = np.int32(42)
        cleaned = to_canonical(val)
        self.assertEqual(cleaned, 42)
        self.assertIsInstance(cleaned, int)

    def test_to_canonical_for_dict(self):
        data = {"a": np.int32(5), "b": [1, 2]}
        cleaned = to_canonical(data)
        self.assertEqual(cleaned, {"a": 5, "b": [1, 2]})

    def test_to_canonical_for_list(self):
        data = [np.int32(1), np.array([2, 3])]
        cleaned = to_canonical(data)
        self.assertEqual(
            cleaned, [1, {"__ndarray__": [2, 3], "dtype": "int64", "shape": (2,)}]
        )

    def test_to_canonical_for_tuple(self):
        data = (np.int32(1), np.array([2, 3]))
        cleaned = to_canonical(data)
        self.assertEqual(
            cleaned, [1, {"__ndarray__": [2, 3], "dtype": "int64", "shape": (2,)}]
        )

    def test_to_canonical_for_set(self):
        data = {np.int32(1), np.int32(2)}
        cleaned = to_canonical(data)
        self.assertEqual(cleaned, [1, 2])

    def test_to_canonical_for_user_defined_object(self):
        class MyObj:
            def __init__(self):
                self.a = np.int32(1)
                self.b = np.array([2, 3])

        obj = MyObj()
        cleaned = to_canonical(obj)
        self.assertEqual(
            cleaned,
            {
                "__class__": "MyObj",
                "__module__": "test_execute_exp.test_services.test_serializers.test_util",
                "attributes": {
                    "a": 1,
                    "b": {"__ndarray__": [2, 3], "dtype": "int64", "shape": (2,)},
                },
            },
        )

    def test_to_canonical_for_slots(self):
        class MySlot:
            __slots__ = ("a", "b")

            def __init__(self):
                self.a = np.int32(1)
                self.b = np.array([2, 3])

        obj = MySlot()
        cleaned = to_canonical(obj)
        self.assertEqual(
            cleaned,
            {
                "__class__": "MySlot",
                "__slots__": {
                    "a": 1,
                    "b": {"__ndarray__": [2, 3], "dtype": "int64", "shape": (2,)},
                },
            },
        )

    def test_to_canonical_for_primitive_type(self):
        for val in [42, "string", 3.14, True, None]:
            self.assertIs(to_canonical(val), val)


if __name__ == "__main__":
    unittest.main()
