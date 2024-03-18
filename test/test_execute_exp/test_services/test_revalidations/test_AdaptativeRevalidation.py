import unittest, os, sys
from unittest.mock import patch, Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.revalidations.AdaptativeRevalidation import AdaptativeRevalidation
from execute_exp.services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from execute_exp.entitites.FunctionCallProv import FunctionCallProv

class TestAdaptativeRevalidation(unittest.TestCase):
    def setUp(self):
        self.execution_mode = Mock(AbstractExecutionMode)
        self.get_function_call_prov_entry_namespace = 'execute_exp.services.revalidations.AbstractRevalidation.DataAccess.get_function_call_prov_entry'
        self.create_or_update_function_call_prov_entry_namespace = 'execute_exp.services.revalidations.AbstractRevalidation.DataAccess.create_or_update_function_call_prov_entry'
        self.fc_prov = FunctionCallProv('', {})

    def test_calculate_next_revalidation_when_adaptative_factor_is_0_and_function_acts_as_expected(self):
        self.execution_mode.func_call_acted_as_expected = Mock(return_value=True)
        adaptativeRevalidation = AdaptativeRevalidation(self.execution_mode, 10, 0)
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_function_call_prov_entry, \
             patch(self.create_or_update_function_call_prov_entry_namespace) as create_or_update_function_call_prov_entry:
            for i in range(1, 6, 1):
                self.fc_prov.next_revalidation = None
                adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
                self.assertEqual(get_function_call_prov_entry.call_count, i)
                self.assertEqual(create_or_update_function_call_prov_entry.call_count, i)
                self.assertEqual(self.fc_prov.next_revalidation, 10)

    def test_calculate_next_revalidation_when_adaptative_factor_is_0_and_function_acts_unexpectedly(self):
        self.execution_mode.func_call_acted_as_expected = Mock(return_value=False)
        adaptativeRevalidation = AdaptativeRevalidation(self.execution_mode, 10, 0)
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_function_call_prov_entry, \
             patch(self.create_or_update_function_call_prov_entry_namespace) as create_or_update_function_call_prov_entry:
            for i in range(1, 6, 1):
                self.fc_prov.next_revalidation = None
                adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
                self.assertEqual(get_function_call_prov_entry.call_count, i)
                self.assertEqual(create_or_update_function_call_prov_entry.call_count, i)
                self.assertEqual(self.fc_prov.next_revalidation, 10)

    def test_calculate_next_revalidation_when_function_acts_as_expected(self):
        self.execution_mode.func_call_acted_as_expected = Mock(return_value=True)
        adaptativeRevalidation = AdaptativeRevalidation(self.execution_mode, 10, 0.5)
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_function_call_prov_entry, \
             patch(self.create_or_update_function_call_prov_entry_namespace) as create_or_update_function_call_prov_entry:
            self.fc_prov.next_revalidation = None
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(get_function_call_prov_entry.call_count, 1)
            self.assertEqual(create_or_update_function_call_prov_entry.call_count, 1)
            self.assertEqual(self.fc_prov.next_revalidation, 15)

            self.fc_prov.next_revalidation = None
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(get_function_call_prov_entry.call_count, 2)
            self.assertEqual(create_or_update_function_call_prov_entry.call_count, 2)
            self.assertEqual(self.fc_prov.next_revalidation, 22)

            self.fc_prov.next_revalidation = None
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(get_function_call_prov_entry.call_count, 3)
            self.assertEqual(create_or_update_function_call_prov_entry.call_count, 3)
            self.assertEqual(self.fc_prov.next_revalidation, 33)

    def test_calculate_next_revalidation_when_function_acts_unexpectedly(self):
        self.execution_mode.func_call_acted_as_expected = Mock(return_value=False)
        adaptativeRevalidation = AdaptativeRevalidation(self.execution_mode, 10, 0.5)
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_function_call_prov_entry, \
             patch(self.create_or_update_function_call_prov_entry_namespace) as create_or_update_function_call_prov_entry:
            self.fc_prov.next_revalidation = None
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(get_function_call_prov_entry.call_count, 1)
            self.assertEqual(create_or_update_function_call_prov_entry.call_count, 1)
            self.assertEqual(self.fc_prov.next_revalidation, 5)

            self.fc_prov.next_revalidation = None
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(get_function_call_prov_entry.call_count, 2)
            self.assertEqual(create_or_update_function_call_prov_entry.call_count, 2)
            self.assertEqual(self.fc_prov.next_revalidation, 2)

            self.fc_prov.next_revalidation = None
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(get_function_call_prov_entry.call_count, 3)
            self.assertEqual(create_or_update_function_call_prov_entry.call_count, 3)
            self.assertEqual(self.fc_prov.next_revalidation, 1)

    def test_calculate_next_revalidation_when_function_behaviour_varies(self):
        self.execution_mode.func_call_acted_as_expected = Mock(return_value=True)
        adaptativeRevalidation = AdaptativeRevalidation(self.execution_mode, 10, 0.5)
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_function_call_prov_entry, \
             patch(self.create_or_update_function_call_prov_entry_namespace) as create_or_update_function_call_prov_entry:
            self.fc_prov.next_revalidation = None
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(get_function_call_prov_entry.call_count, 1)
            self.assertEqual(create_or_update_function_call_prov_entry.call_count, 1)
            self.assertEqual(self.fc_prov.next_revalidation, 15)

            self.execution_mode.func_call_acted_as_expected = Mock(return_value=False)
            self.fc_prov.next_revalidation = None
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(get_function_call_prov_entry.call_count, 2)
            self.assertEqual(create_or_update_function_call_prov_entry.call_count, 2)
            self.assertEqual(self.fc_prov.next_revalidation, 8)

            self.fc_prov.next_revalidation = None
            adaptativeRevalidation.calculate_next_revalidation('function_call_hash', None)
            self.assertEqual(get_function_call_prov_entry.call_count, 3)
            self.assertEqual(create_or_update_function_call_prov_entry.call_count, 3)
            self.assertEqual(self.fc_prov.next_revalidation, 4)

if __name__ == '__main__':
    unittest.main()