import unittest

import numpy as np
import pandas as pd

from execute_exp.services.serializers.util import to_canonical

# The canonical form of np.array([2, 3]): a header and the buffer, as bytes.
ARRAY_2_3 = {
    "__ndarray__": np.array([2, 3]).tobytes(),
    "dtype": np.array([2, 3]).dtype.descr,
    "shape": (2,),
}


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
            cleaned,
            {
                "__ndarray__": arr.tobytes(),
                "dtype": arr.dtype.descr,
                "shape": (3,),
            },
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
        self.assertEqual(cleaned, [1, ARRAY_2_3])

    def test_to_canonical_for_tuple(self):
        data = (np.int32(1), np.array([2, 3]))
        cleaned = to_canonical(data)
        self.assertEqual(cleaned, [1, ARRAY_2_3])

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
                    "b": ARRAY_2_3,
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
                    "b": ARRAY_2_3,
                },
            },
        )

    def test_to_canonical_for_primitive_type(self):
        for val in [42, "string", 3.14, True, None]:
            self.assertIs(to_canonical(val), val)


class TestToCanonicalCycles(unittest.TestCase):
    def test_repeated_primitives_are_not_cycles(self):
        self.assertEqual(to_canonical([1, 2, 1]), [1, 2, 1])
        self.assertEqual(to_canonical(("a", "a", None, None)), ["a", "a", None, None])

    def test_the_same_container_twice_is_not_a_cycle(self):
        shared = [1, 2]
        self.assertEqual(to_canonical([shared, shared]), [[1, 2], [1, 2]])

    def test_a_list_that_contains_itself_gets_the_cycle_marker(self):
        loop = [1]
        loop.append(loop)
        self.assertEqual(to_canonical(loop), [1, "<CYCLE>"])


class TestToCanonicalPandas(unittest.TestCase):
    def test_dataframes_with_different_values_differ(self):
        a = pd.DataFrame({"x": [1, 2, 3], "y": [4.0, 5.0, 6.0]})
        b = pd.DataFrame({"x": [1, 2, 4], "y": [4.0, 5.0, 6.0]})
        self.assertNotEqual(to_canonical(a), to_canonical(b))

    def test_dataframes_with_different_columns_differ(self):
        a = pd.DataFrame({"x": [1, 2]})
        b = pd.DataFrame({"z": [1, 2]})
        self.assertNotEqual(to_canonical(a), to_canonical(b))

    def test_dataframes_with_different_dtypes_differ(self):
        a = pd.DataFrame({"x": [1, 2]})
        b = pd.DataFrame({"x": [1.0, 2.0]})
        self.assertNotEqual(to_canonical(a), to_canonical(b))

    def test_dataframes_with_different_index_differ(self):
        a = pd.DataFrame({"x": [1, 2]}, index=[0, 1])
        b = pd.DataFrame({"x": [1, 2]}, index=[5, 6])
        self.assertNotEqual(to_canonical(a), to_canonical(b))

    def test_the_same_dataframe_twice_is_equal(self):
        def build():
            return pd.DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})

        self.assertEqual(to_canonical(build()), to_canonical(build()))

    def test_series_with_different_values_differ(self):
        self.assertNotEqual(
            to_canonical(pd.Series([1, 2, 3])), to_canonical(pd.Series([1, 2, 4]))
        )

    def test_series_with_different_lengths_differ(self):
        self.assertNotEqual(
            to_canonical(pd.Series([1, 2, 3])), to_canonical(pd.Series([1, 2]))
        )

    def test_the_same_series_twice_is_equal(self):
        self.assertEqual(
            to_canonical(pd.Series([1.5, 2.5], name="s")),
            to_canonical(pd.Series([1.5, 2.5], name="s")),
        )

    def test_index_with_different_values_differ(self):
        self.assertNotEqual(
            to_canonical(pd.Index([1, 2, 3])), to_canonical(pd.Index([1, 2, 4]))
        )

    def test_timestamps_differ_and_repeat(self):
        a = pd.Timestamp("2024-01-01 10:00:00")
        b = pd.Timestamp("2024-01-02 10:00:00")
        self.assertNotEqual(to_canonical(a), to_canonical(b))
        self.assertEqual(to_canonical(a), to_canonical(pd.Timestamp(a)))

    def test_timedeltas_differ_and_repeat(self):
        a = pd.Timedelta(hours=1)
        b = pd.Timedelta(hours=2)
        self.assertNotEqual(to_canonical(a), to_canonical(b))
        self.assertEqual(to_canonical(a), to_canonical(pd.Timedelta(hours=1)))


class TestToCanonicalPrivateState(unittest.TestCase):
    def test_instances_with_different_private_state_differ(self):
        class Box:
            def __init__(self, value):
                self._value = value

        self.assertNotEqual(to_canonical(Box(1)), to_canonical(Box(2)))

    def test_instances_with_the_same_private_state_are_equal(self):
        class Box:
            def __init__(self, value):
                self._value = value

        self.assertEqual(to_canonical(Box([1, 2])), to_canonical(Box([1, 2])))

    def test_object_without_a_known_form_is_not_stringified(self):
        class Odd:
            __slots__ = ()

            def __repr__(self):
                return "same repr"

        self.assertNotEqual(to_canonical(complex(1, 2)), "(1+2j)")
        self.assertIsInstance(to_canonical(complex(1, 2)), bytes)
        self.assertNotEqual(to_canonical(range(3)), to_canonical(range(4)))


class TestToCanonicalNumpy(unittest.TestCase):
    def test_the_same_array_twice_is_equal(self):
        self.assertEqual(
            to_canonical(np.arange(6.0).reshape(2, 3)),
            to_canonical(np.arange(6.0).reshape(2, 3)),
        )

    def test_another_dtype_differs(self):
        self.assertNotEqual(
            to_canonical(np.array([1, 2, 3], dtype=np.int32)),
            to_canonical(np.array([1, 2, 3], dtype=np.int64)),
        )

    def test_another_shape_differs(self):
        a = np.arange(6)
        self.assertNotEqual(
            to_canonical(a.reshape(2, 3)), to_canonical(a.reshape(3, 2))
        )

    def test_another_byte_order_differs(self):
        little = np.array([1, 2, 3], dtype="<i4")
        big = np.array([1, 2, 3], dtype=">i4")
        self.assertNotEqual(to_canonical(little), to_canonical(big))

    def test_one_element_changed_differs(self):
        a = np.arange(10.0)
        b = a.copy()
        b[7] += 1e-9
        self.assertNotEqual(to_canonical(a), to_canonical(b))

    def test_a_non_contiguous_view_equals_its_contiguous_copy(self):
        base = np.arange(12.0).reshape(3, 4)
        view = base[:, ::2]
        self.assertFalse(view.flags["C_CONTIGUOUS"])
        self.assertEqual(to_canonical(view), to_canonical(np.ascontiguousarray(view)))

    def test_the_bytes_are_bytes_not_a_list(self):
        form = to_canonical(np.arange(3, dtype="<i8"))
        self.assertIsInstance(form, dict)
        self.assertIn(np.arange(3, dtype="<i8").tobytes(), form.values())

    def test_structured_arrays_differing_only_in_field_names_differ(self):
        a = np.zeros(2, dtype=[("x", "<i4"), ("y", "<f8")])
        b = np.zeros(2, dtype=[("u", "<i4"), ("v", "<f8")])
        self.assertEqual(a.dtype.itemsize, b.dtype.itemsize)
        self.assertEqual(a.tobytes(), b.tobytes())
        self.assertNotEqual(to_canonical(a), to_canonical(b))
        self.assertEqual(
            to_canonical(a),
            to_canonical(np.zeros(2, dtype=[("x", "<i4"), ("y", "<f8")])),
        )

    def test_object_dtype_array_still_works(self):
        a = np.array([1, "a", None, (2, 3)], dtype=object)
        b = np.array([1, "a", None, (2, 4)], dtype=object)
        self.assertEqual(to_canonical(a), to_canonical(a.copy()))
        self.assertNotEqual(to_canonical(a), to_canonical(b))


if __name__ == "__main__":
    unittest.main()
