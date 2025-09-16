from unittest.mock import patch
import unittest, os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from execute_exp.services.factory import get_serializer, init_revalidation, init_exec_mode
from execute_exp.services.serializers.PickleSerializer import PickleSerializer
from execute_exp.services.serializers.CloudpickleSerializer import CloudpickleSerializer
from execute_exp.services.execution_modes.AccurateMode import AccurateMode
from execute_exp.services.execution_modes.ProbabilisticCountingMode import ProbabilisticCountingMode
from execute_exp.services.execution_modes.ProbabilisticErrorMode import ProbabilisticErrorMode
from execute_exp.services.revalidations.NoRevalidation import NoRevalidation
from execute_exp.services.revalidations.FixedRevalidation import FixedRevalidation
from execute_exp.services.revalidations.AdaptativeRevalidation import AdaptativeRevalidation
import sys, random


class TestFactory(unittest.TestCase):
    @patch("execute_exp.services.factory.SpeeduPySettings")
    def test_init_exec_mode(self, SpeeduPySettings):
        exec_mode = random.choice([['no-cache', None],
                                   ['manual', None],
                                   ['accurate', AccurateMode],
                                   ['probabilistic-counting', ProbabilisticCountingMode],
                                   ['probabilistic-error', ProbabilisticErrorMode]])
        SpeeduPySettings().exec_mode = [exec_mode[0]]
        serializer = random.choice([['pickle', PickleSerializer],
                                    ['cloudpickle', CloudpickleSerializer]])
        SpeeduPySettings().serializer = [serializer[0]]
        SpeeduPySettings().min_num_exec = random.randint(10, 50)
        SpeeduPySettings().min_mode_occurrence = random.random()
        SpeeduPySettings().max_error_per_function = random.randint(10, 50)
        SpeeduPySettings().confidence_lv = random.random()

        result = init_exec_mode()

        self.assertIsInstance(result, exec_mode[1])
        if exec_mode[1] is not None:
            self.assertIsInstance(result._serializer, serializer[1])
            self.assertEqual(result._min_num_exec, SpeeduPySettings().min_num_exec)
        elif exec_mode[1] == ProbabilisticCountingMode:
            self.assertEqual(result._ProbabilisticCountingMode__min_mode_occurrence, SpeeduPySettings().min_mode_occurrence)
        elif exec_mode[1] == ProbabilisticErrorMode:
            self.assertEqual(result._ProbabilisticErrorMode__max_error_per_function, SpeeduPySettings().max_error_per_function)
            self.assertEqual(result._ProbabilisticErrorMode__confidence_lv, SpeeduPySettings().confidence_lv)
    
    @patch("execute_exp.services.factory.SpeeduPySettings")
    def test_init_revalidation_when_exec_mode_is_none(self, SpeeduPySettings):
        exec_mode = None
        revalidation = random.choice(['none', 'fixed', 'adaptative'])
        SpeeduPySettings().revalidation = revalidation
        self.assertIsNone(init_revalidation(exec_mode))
    
    @patch("execute_exp.services.factory.SpeeduPySettings")
    def test_init_revalidation_when_exec_mode_is_not_none(self, SpeeduPySettings):
        exec_mode = random.choice([AccurateMode, ProbabilisticCountingMode, ProbabilisticErrorMode])
        revalidation = random.choice([['none', NoRevalidation],
                                      ['fixed', FixedRevalidation],
                                      ['adaptative', AdaptativeRevalidation]])
        SpeeduPySettings().revalidation = [revalidation[0]]
        SpeeduPySettings().max_num_exec_til_reval = random.randint(10, 50)
        SpeeduPySettings().reduction_factor = random.random()

        result = init_revalidation(exec_mode)

        self.assertIsInstance(result, revalidation[1])
        if revalidation[1] == FixedRevalidation:
            self.assertEqual(result._FixedRevalidation__fixed_num_exec_til_reval, SpeeduPySettings().max_num_exec_til_reval)
        elif revalidation[1] == AdaptativeRevalidation:
            self.assertEqual(result._AdaptativeRevalidation__current_num_exec_til_reval, SpeeduPySettings().max_num_exec_til_reval)
            self.assertEqual(result._AdaptativeRevalidation__adaptative_factor, SpeeduPySettings().reduction_factor)

    @patch("execute_exp.services.factory.SpeeduPySettings")
    def test_get_serializer(self, SpeeduPySettings):
        serializer = random.choice([['pickle', PickleSerializer],
                                    ['cloudpickle', CloudpickleSerializer]])
        SpeeduPySettings().serializer = [serializer[0]]
        self.assertIsInstance(get_serializer(), serializer[1])

if __name__ == '__main__':
    unittest.main()