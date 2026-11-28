import json
import unittest
from unittest.mock import Mock

import xxhash

from execute_exp.services.hashes.XXHashHash import XXHashHash


class TestXXHashHash(unittest.TestCase):
    def setUp(self):
        self.serializer = Mock()
        self.hash = XXHashHash(self.serializer)

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
        expected_result = xxhash.xxh128_hexdigest(data)

        self.assertEqual(result, expected_result)

    def test_the_digest_is_xxh3_128(self):
        # A literal value: a digest that changes between releases silently
        # empties every cache.
        result = self.hash._hash(b"speedupy")

        self.assertEqual(result, "6efc8be7919cabbd9e2ca3dc7a53b0d1")


if __name__ == "__main__":
    unittest.main()
