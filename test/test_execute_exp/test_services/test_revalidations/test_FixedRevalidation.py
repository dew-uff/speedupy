import unittest, os, sys
from unittest.mock import patch

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.revalidations.FixedRevalidation import FixedRevalidation
from execute_exp.entitites.FunctionCallProv import FunctionCallProv
class TestFixedRevalidation(unittest.TestCase):
    def setUp(self):
        self.get_function_call_prov_entry_namespace = 'execute_exp.services.revalidations.AbstractRevalidation.DataAccess.get_function_call_prov_entry'
        self.create_or_update_function_call_prov_entry_namespace = 'execute_exp.services.revalidations.AbstractRevalidation.DataAccess.create_or_update_function_call_prov_entry'
        self.fc_prov = FunctionCallProv('', {})

    def test_calculate_next_revalidation(self):
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_function_call_prov_entry, \
             patch(self.create_or_update_function_call_prov_entry_namespace) as create_or_update_function_call_prov_entry:
            for i in range(1, 16, 1):
                self.fixedRevalidation = FixedRevalidation(i)

                self.fc_prov.next_revalidation = None
                self.fixedRevalidation.calculate_next_revalidation(f'function_call_hash_{i}', None)
                self.assertEqual(get_function_call_prov_entry.call_count, 2*i - 1)
                self.assertEqual(create_or_update_function_call_prov_entry.call_count, 2*i - 1)
                self.assertEqual(self.fc_prov.next_revalidation, i)

                self.fc_prov.next_revalidation = None
                self.fixedRevalidation.calculate_next_revalidation(f'fchash_{i}', None)
                self.assertEqual(get_function_call_prov_entry.call_count, 2*i)
                self.assertEqual(create_or_update_function_call_prov_entry.call_count, 2*i)
                self.assertEqual(self.fc_prov.next_revalidation, i)

if __name__ == '__main__':
    unittest.main()