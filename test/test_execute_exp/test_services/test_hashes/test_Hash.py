import json
import os
import unittest
from unittest.mock import Mock, call

from execute_exp.services.hashes.Hash import Hash
from execute_exp.services.hashes.XXHashHash import XXHashHash
from execute_exp.services.serializers.PickleSerializer import PickleSerializer


class TestHash(unittest.TestCase):
    def setUp(self):
        self.first_dumps_output = os.urandom(16)
        self.second_dumps_output = os.urandom(16)
        self.serializer = Mock()
        self.serializer.dumps = Mock(
            side_effect=[self.first_dumps_output, self.second_dumps_output]
        )
        self.serializer.to_canonical = Mock(side_effect=lambda x: x)

        self.hash = Hash(self.serializer)

        self.hash._hash = Mock()

    def test_get_id_without_fun_args(self):
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'

        self.hash.get_id(source, fun_kwargs={"z": -12.5})

        self.assertEqual(self.serializer.to_canonical.call_count, 2)
        self.assertEqual(
            self.serializer.to_canonical.call_args_list, [call(()), call({"z": -12.5})]
        )
        expected_args = json.dumps(
            {"args": [], "kwargs": {"z": -12.5}, "source": source},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.hash._hash.assert_called_once_with(expected_args)

    def test_get_id_without_fun_kwargs(self):
        source = 'print("Testando!")\nos.path.exists("/")\nrandom.randint()\nreturn x + y / -z'

        self.hash.get_id(source, fun_args=[-1.227, 0])

        self.assertEqual(self.serializer.to_canonical.call_count, 2)
        self.assertEqual(
            self.serializer.to_canonical.call_args_list, [call([-1.227, 0]), call({})]
        )
        expected_args = json.dumps(
            {"args": [-1.227, 0], "kwargs": {}, "source": source},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.hash._hash.assert_called_once_with(expected_args)

    def test_get_id_only_with_fun_source(self):
        source = 'print("Testando!")\nreturn x / y ** 2'

        self.hash.get_id(source)

        self.assertEqual(self.serializer.to_canonical.call_count, 2)
        self.assertEqual(
            self.serializer.to_canonical.call_args_list, [call(()), call({})]
        )
        expected_args = json.dumps(
            {"args": [], "kwargs": {}, "source": source},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.hash._hash.assert_called_once_with(expected_args)

    def test_get_id_with_source_args_and_kwargs(self):
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'

        self.hash.get_id(source, fun_args=[-1.227, 0], fun_kwargs={"z": -12.5})

        self.assertEqual(self.serializer.to_canonical.call_count, 2)
        self.serializer.to_canonical.assert_has_calls(
            [call([-1.227, 0]), call({"z": -12.5})]
        )
        expected_args = json.dumps(
            {"args": [-1.227, 0], "kwargs": {"z": -12.5}, "source": source},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.hash._hash.assert_called_once_with(expected_args)

    def test_get_id_default_kwargs_are_not_shared_between_calls(self):
        seen_kwargs = []

        def record_then_mutate(obj):
            if isinstance(obj, dict):
                seen_kwargs.append(dict(obj))
                obj["leaked"] = True
            return obj

        self.serializer.to_canonical = Mock(side_effect=record_then_mutate)

        self.hash.get_id("return 1")
        self.hash.get_id("return 1")

        self.assertEqual(seen_kwargs, [{}, {}])


class TestGetIdWithBytesLeaves(unittest.TestCase):
    def test_bytes_leaves_follow_the_json_text_in_a_fixed_order(self):
        serializer = Mock()
        serializer.to_canonical = Mock(
            side_effect=[[b"AAA", {"b": b"CC", "a": b"D"}], {}]
        )
        hash_ = Hash(serializer)
        hash_._hash = Mock()

        hash_.get_id("src", (1,))

        text = json.dumps(
            {
                "args": [
                    {"__bytes__": 0, "length": 3},
                    {
                        "a": {"__bytes__": 1, "length": 1},
                        "b": {"__bytes__": 2, "length": 2},
                    },
                ],
                "kwargs": {},
                "source": "src",
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        hash_._hash.assert_called_once_with(text + b"\x00" + b"AAA" + b"D" + b"CC")


class TestGetIdWithTheRealCanonicalForm(unittest.TestCase):
    def setUp(self):
        self.hash = XXHashHash(PickleSerializer())

    def test_repeated_primitive_arguments_give_different_ids(self):
        # #74: f(1, 2, 1) and f(1, 2, 2) shared one key.
        self.assertNotEqual(
            self.hash.get_id("src", (1, 2, 1)), self.hash.get_id("src", (1, 2, 2))
        )

    def test_the_same_call_twice_gives_the_same_id(self):
        self.assertEqual(
            self.hash.get_id("src", (1, 2, 1), {"k": "v"}),
            self.hash.get_id("src", (1, 2, 1), {"k": "v"}),
        )

    def test_the_source_is_part_of_the_id(self):
        self.assertNotEqual(self.hash.get_id("a", (1,)), self.hash.get_id("b", (1,)))

    def test_dataframes_with_different_values_give_different_ids(self):
        import pandas as pd

        a = pd.DataFrame({"x": [1, 2, 3]})
        b = pd.DataFrame({"x": [1, 2, 4]})
        self.assertNotEqual(
            self.hash.get_id("src", (a,)), self.hash.get_id("src", (b,))
        )
        self.assertEqual(
            self.hash.get_id("src", (a,)), self.hash.get_id("src", (a.copy(),))
        )

    def test_arrays_give_ids_that_follow_their_content(self):
        import numpy as np

        a = np.arange(1000.0)
        b = a.copy()
        b[999] = -1
        self.assertEqual(
            self.hash.get_id("src", (a,)), self.hash.get_id("src", (a.copy(),))
        )
        self.assertNotEqual(
            self.hash.get_id("src", (a,)), self.hash.get_id("src", (b,))
        )
        self.assertNotEqual(
            self.hash.get_id("src", (a,)),
            self.hash.get_id("src", (a.astype(np.float32),)),
        )

    def test_the_leaf_bytes_cannot_be_confused_with_text(self):
        # A bytes leaf and a string with the same characters are not one key.
        self.assertNotEqual(
            self.hash.get_id("src", (complex(1, 2),)),
            self.hash.get_id("src", ("(1+2j)",)),
        )


if __name__ == "__main__":
    unittest.main()
