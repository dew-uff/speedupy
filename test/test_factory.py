from unittest.mock import patch
import unittest, os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from execute_exp.services.factory import get_serializer
from execute_exp.services.serializers.PickleSerializer import PickleSerializer
from execute_exp.services.serializers.CloudpickleSerializer import CloudpickleSerializer
import sys, random


class TestFactory(unittest.TestCase):
    @patch("execute_exp.services.factory.SpeeduPySettings")
    def test_get_serializer(self, SpeeduPySettings):
        serializer = random.choice([['pickle', PickleSerializer],
                                    ['cloudpickle', CloudpickleSerializer]])
        SpeeduPySettings().serializer = [serializer[0]]
        self.assertIsInstance(get_serializer(), serializer[1])

if __name__ == '__main__':
    unittest.main()