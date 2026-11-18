import unittest
from unittest.mock import Mock

from execute_exp.services.hashes.A5Hash import A5Hash


class TestA5Hash(unittest.TestCase):
    def setUp(self):
        # Mocks to simulate the serialization of args and kwargs
        self.serializer = Mock()
        self.serializer.to_canonical = Mock(side_effect=lambda x: x)

        self.hash = A5Hash(self.serializer)

    def test_hash_consistency(self):
        """
        Testa se o mesmo input produz o mesmo hash (Estabilidade).
        """
        source = "def minha_funcao(): return 42"
        args = [1, 2, 3]
        kwargs = {"a": "b"}

        hash1 = self.hash.get_id(source, fun_args=args, fun_kwargs=kwargs)
        hash2 = self.hash.get_id(source, fun_args=args, fun_kwargs=kwargs)

        self.assertEqual(
            hash1,
            hash2,
            "The same input did not produce identical hashes (stability failure).",
        )
        self.assertEqual(
            len(hash1),
            16,
            "The hash does not have the correct length (16 hex characters).",
        )
        self.assertTrue(
            all(c in "0123456789abcdef" for c in hash1),
            "The hash contains non-hexadecimal characters.",
        )

    def test_hash_non_collision(self):
        """
        Tests that different inputs produce different hashes (no collision).
        """
        source1 = "def f(x): return x + 1"
        source2 = "def f(x): return x + 2"

        # --- Call 1: hash1 (Args: [5]) ---
        hash1 = self.hash.get_id(source1, fun_args=[5])

        # --- Call 2: hash2 (Source changes) ---
        hash2 = self.hash.get_id(source2, fun_args=[5])

        # --- Call 3: hash3 (Args change to [6]) ---
        hash3 = self.hash.get_id(source1, fun_args=[6])

        # Test 1: Source change (hash1 vs hash2).
        self.assertNotEqual(
            hash1, hash2, "Different source codes produced the same hash (collision)."
        )

        # Test 2: Arg change (hash1 vs hash3).
        self.assertNotEqual(
            hash1, hash3, "Different arguments produced the same hash (collision)."
        )

        # Test 3: Mixed change (hash2 vs hash3).
        self.assertNotEqual(
            hash2, hash3, "Different inputs produced the same hash (collision)."
        )


if __name__ == "__main__":
    unittest.main()
