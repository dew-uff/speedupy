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

    def test_calculate_next_revalidation(self):
        with patch(self.create_or_update_function_call_prov_entry_namespace) as create_or_update_function_call_prov_entry:
            for i in range(1, 16, 1):
                self.fixedRevalidation = FixedRevalidation(i)

                fc_prov = FunctionCallProv(f'function_call_hash_{i}', {})
                fc_prov.next_revalidation = None
                self.fixedRevalidation.calculate_next_revalidation(fc_prov, None)
                self.assertEqual(create_or_update_function_call_prov_entry.call_count, 2*i - 1)
                self.assertEqual(fc_prov.next_revalidation, i)

                fc_prov = FunctionCallProv(f'fc_hash_{i}', {})
                fc_prov.next_revalidation = None
                self.fixedRevalidation.calculate_next_revalidation(fc_prov, None)
                self.assertEqual(create_or_update_function_call_prov_entry.call_count, 2*i)
                self.assertEqual(fc_prov.next_revalidation, i)

if __name__ == '__main__':
    unittest.main()