import unittest, os, sys
from types import FunctionType
import numpy as np

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.serializers.util import clean_data


class TestUtil(unittest.TestCase):
    def test_clean_data_for_function_with_globals_file_atribute(self):
        g = {"__file__": "somefile.py", "x": 42}
        def f(): return g["x"]
        f.__globals__.update(g)

        cleaned = clean_data(f)
        self.assertIsNot(cleaned, f)
        self.assertIsInstance(cleaned, FunctionType)
        self.assertIsNone(cleaned.__globals__.get("__file__"))
        self.assertEqual(cleaned.__globals__["x"], 42)

    def test_clean_data_for_function_without_globals_file_atribute(self):
        g = {"y": 100}
        code = "def f(): return y"
        exec(code, g)
        f = g["f"]
        cleaned = clean_data(f)
        self.assertIs(cleaned, f)
        self.assertDictEqual(cleaned.__globals__, g)

    def test_clean_data_for_numpy_ndarray(self):
        arr = np.array([1, 2, 3])
        cleaned = clean_data(arr)
        self.assertEqual(cleaned, [1, 2, 3])
        self.assertIsInstance(cleaned, list)

    def test_clean_data_for_numpy_generic(self):
        val = np.int32(42)
        cleaned = clean_data(val)
        self.assertEqual(cleaned, 42)
        self.assertIsInstance(cleaned, int)

    def test_clean_data_for_dict(self):
        data = {"a": np.int32(5), "b": [1, 2]}
        cleaned = clean_data(data)
        self.assertEqual(cleaned, {"a": 5, "b": [1, 2]})

    def test_clean_data_for_list(self):
        data = [np.int32(1), np.array([2, 3])]
        cleaned = clean_data(data)
        self.assertEqual(cleaned, [1, [2, 3]])

    def test_clean_data_for_tuple(self):
        data = (np.int32(1), np.array([2, 3]))
        cleaned = clean_data(data)
        self.assertEqual(cleaned, (1, [2, 3]))

    def test_clean_data_for_set(self):
        data = {np.int32(1), np.int32(2)}
        cleaned = clean_data(data)
        self.assertEqual(cleaned, {1, 2})

    def test_clean_data_for_user_defined_object(self):
        class MyObj:
            def __init__(self):
                self.a = np.int32(1)
                self.b = np.array([2, 3])
        obj = MyObj()
        cleaned = clean_data(obj)
        self.assertIs(cleaned, obj)
        self.assertEqual(obj.a, 1)
        self.assertEqual(obj.b, [2, 3])

    def test_clean_data_for_slots(self):
        class MySlot:
            __slots__ = ("a", "b")

            def __init__(self):
                self.a = np.int32(1)
                self.b = np.array([2, 3])

        obj = MySlot()
        cleaned = clean_data(obj)
        self.assertIs(cleaned, obj)
        self.assertEqual(obj.a, 1)
        self.assertEqual(obj.b, [2, 3])

    def test_clean_data_for_primitive_type(self):
        for val in [42, "string", 3.14, True, None]:
            self.assertIs(clean_data(val), val)


if __name__ == '__main__':
    unittest.main()
