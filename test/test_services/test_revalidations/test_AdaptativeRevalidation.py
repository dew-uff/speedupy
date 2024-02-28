import unittest, os, sys
from unittest.mock import patch, Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from services.revalidations.AdaptativeRevalidation import AdaptativeRevalidation
from services.execution_modes.AbstractExecutionMode import AbstractExecutionMode

class TestAdaptativeRevalidation(unittest.TestCase):
    def setUp(self):
        self.execution_mode = Mock(AbstractExecutionMode)
        self.get_func_call_prov_attr_namespace = 'services.revalidations.AbstractRevalidation.get_func_call_prov_attr'
        self.set_func_call_prov_attr_namespace = 'services.revalidations.AbstractRevalidation.set_func_call_prov_attr'

    def test_calculate_next_revalidation_when_adaptative_factor_is_0_and_function_acts_as_expected(self):
        self.execution_mode.function_acted_as_expected = Mock(return_value=True)
        adaptativeRevalidation = AdaptativeRevalidation(self.execution_mode, 10, 0)
        with patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            for i in range(1, 6, 1):
                adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
                self.assertEqual(set_func_call_prov_attr.call_count, i)
                args = set_func_call_prov_attr.call_args.args
                self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 10))

    def test_calculate_next_revalidation_when_adaptative_factor_is_0_and_function_acts_unexpectedly(self):
        self.execution_mode.function_acted_as_expected = Mock(return_value=False)
        adaptativeRevalidation = AdaptativeRevalidation(self.execution_mode, 10, 0)
        with patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            for i in range(1, 6, 1):
                adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
                self.assertEqual(set_func_call_prov_attr.call_count, i)
                args = set_func_call_prov_attr.call_args.args
                self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 10))

    def test_calculate_next_revalidation_when_function_acts_as_expected(self):
        self.execution_mode.function_acted_as_expected = Mock(return_value=True)
        adaptativeRevalidation = AdaptativeRevalidation(self.execution_mode, 10, 0.5)
        with patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(set_func_call_prov_attr.call_count, 1)
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 15))

            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(set_func_call_prov_attr.call_count, 2)
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 22))

            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(set_func_call_prov_attr.call_count, 3)
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 33))

    def test_calculate_next_revalidation_when_function_acts_unexpectedly(self):
        self.execution_mode.function_acted_as_expected = Mock(return_value=False)
        adaptativeRevalidation = AdaptativeRevalidation(self.execution_mode, 10, 0.5)
        with patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(set_func_call_prov_attr.call_count, 1)
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 5))

            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(set_func_call_prov_attr.call_count, 2)
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 2))

            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(set_func_call_prov_attr.call_count, 3)
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 1))

    def test_calculate_next_revalidation_when_function_behaviour_varies(self):
        self.execution_mode.function_acted_as_expected = Mock(return_value=True)
        adaptativeRevalidation = AdaptativeRevalidation(self.execution_mode, 10, 0.5)
        with patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(set_func_call_prov_attr.call_count, 1)
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 15))

            self.execution_mode.function_acted_as_expected = Mock(return_value=False)
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(set_func_call_prov_attr.call_count, 2)
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 8))

            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(set_func_call_prov_attr.call_count, 3)
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('function_call_hash', 'next_revalidation', 4))

if __name__ == '__main__':
    unittest.main()