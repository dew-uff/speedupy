import json
import unittest
from unittest.mock import Mock

import mmh3

from execute_exp.services.hashes.MurmurHash import MurmurHash


class TestMurmurHash(unittest.TestCase):
    def setUp(self):
        self.serializer = Mock()
        self.hash = MurmurHash(self.serializer)

    def test_get_id_with_source_args_and_kwargs(self):
        fun_args = [-1.227, 0]
        fun_kwargs = {"z": -12.5}
        fun_source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'

        self.serializer.to_canonical = Mock(side_effect=[fun_args, fun_kwargs])

        result = self.hash.get_id(fun_source, fun_args=fun_args, fun_kwargs=fun_kwargs)

        data = json.dumps(
            {"args": fun_args, "kwargs": fun_kwargs, "source": fun_source},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        expected_result = hex(mmh3.hash128(data))[2:]

        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    unittest.main()
