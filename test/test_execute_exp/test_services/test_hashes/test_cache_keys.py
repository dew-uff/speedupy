"""Cache keys do not move with the Python or the numpy version (issue #164).

The literal keys were generated with numpy 1.26.4 and pandas 2.3.3 on Python
3.11, before the pins moved. A different key is a cache that no longer hits.

Some nested numpy values do get another key with numpy 2: they are listed in
issue #170 and are not here. Arrays name their dtype, since the default integer
of numpy 1 on Windows is not that of numpy 2.
"""

import unittest

import numpy as np
import pandas as pd

from execute_exp.services.hashes.XXHashHash import XXHashHash
from execute_exp.services.serializers.PickleSerializer import PickleSerializer

FLOATS = np.arange(12, dtype="float64").reshape(3, 4)
RECORDS = np.array([(1, 2.0)], dtype=[("a", "<i4"), ("b", "<f8")])

# name: (args, kwargs, key)
CASES = {
    "lists_and_kwargs": (
        ([1, 2, 3],),
        {"factor": 2},
        "395506c698a74d905d45a754c3a28fea",
    ),
    "integer": ((20,), {}, "dbf804167ec119637be318e5e846d69b"),
    "string_and_integer": (("a", 1), {}, "018345c039943cb77360e37820da55a5"),
    "float_array": ((FLOATS,), {}, "62912f860120b8c75837ad64558acc20"),
    "fortran_array": (
        (np.asfortranarray(FLOATS),),
        {},
        "62912f860120b8c75837ad64558acc20",
    ),
    "big_endian_array": (
        (np.arange(5, dtype=">i4"),),
        {},
        "39dfc85d9a96dd1f1fec512b921893ff",
    ),
    "bool_array": (
        (np.array([True, False]),),
        {},
        "56d1a0c78577fed9a39fa87d396a9159",
    ),
    "string_array": (
        (np.array(["a", "bb"]),),
        {},
        "5940e01354750b307a502fa11014f163",
    ),
    "datetime_array": (
        (np.array(["2020-01-01"], dtype="datetime64[D]"),),
        {},
        "11f7821392e7ca044b8ee5fb3d3a24be",
    ),
    "object_array": (
        (np.array([1, "a", None, np.float64(1.5)], dtype=object),),
        {},
        "658ecfe5585fa44539e18d117a5bce42",
    ),
    "structured_array": ((RECORDS,), {}, "f663b0704eecbfbc6def7303f1da30ef"),
    "float64": ((np.float64(1.5),), {}, "87faf2ae4ff3b0a4bb4771f771d97dea"),
    "float32": ((np.float32(1.5),), {}, "87faf2ae4ff3b0a4bb4771f771d97dea"),
    "int64": ((np.int64(7),), {}, "2ba0dbca2b92b4e97c3adf3f4436b48c"),
    "numpy_bool": ((np.bool_(True),), {}, "d5232d7bc03a52ce8984ffe844bd5dc7"),
    "numpy_str": ((np.str_("a"),), {}, "b2d949fdc32f2a55b5c15d3b41e60ec6"),
    "set_of_float64": (
        ({np.float64(1.0), np.float64(5.0)},),
        {},
        "c9346457e6732b900767bbdf55262d6a",
    ),
    "float64_dict_key": (
        ({np.float64(1.0): 3},),
        {},
        "1d76b9e15a3329ad0dd991a35bf5ad75",
    ),
    "dtype": ((np.dtype("float64"),), {}, "c43a0f765d1ef8ad0d045426deaab2f5"),
    "integer_dataframe": (
        (pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]}),),
        {},
        "8757bea0e04917cb4f74014e5f1561b6",
    ),
    "integer_series": (
        (pd.Series([1, 2, 3]),),
        {},
        "5866b6b714e1bfa4ee8850035d52066f",
    ),
    "timestamp": (
        (pd.Timestamp("2020-01-01"),),
        {},
        "f0baaa19a0644a1e5135dab82591233d",
    ),
}


class TestCacheKeysAcrossVersions(unittest.TestCase):
    def test_the_keys_are_those_of_numpy_1_26_4(self):
        hash_ = XXHashHash(PickleSerializer())
        for name, (args, kwargs, expected) in CASES.items():
            with self.subTest(name):
                self.assertEqual(hash_.get_id("src", args, kwargs), expected)


if __name__ == "__main__":
    unittest.main()
