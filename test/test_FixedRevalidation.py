import unittest, os, sys
from unittest.mock import patch

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from services.revalidations.FixedRevalidation import FixedRevalidation

class TestFixedRevalidation(unittest.TestCase):
    def setUp(self):
        self.get_func_call_prov_attr_namespace = 'services.revalidations.AbstractRevalidation.get_func_call_prov_attr'
        self.set_func_call_prov_attr_namespace = 'services.revalidations.AbstractRevalidation.set_func_call_prov_attr'

    def test_calculate_next_revalidation(self):
        with patch(self.get_func_call_prov_attr_namespace) as get_func_call_prov_attr, \
             patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            for i in range(1, 16, 1):
                self.fixedRevalidation = FixedRevalidation(i)
                self.fixedRevalidation.calculate_next_revalidation(f'function_call_hash_{i}', None)
                self.assertEqual(set_func_call_prov_attr.call_count, 2*i - 1)
                args = set_func_call_prov_attr.call_args.args
                self.assertTupleEqual(args, (f'function_call_hash_{i}', 'next_revalidation', i))

                self.fixedRevalidation.calculate_next_revalidation(f'fchash_{i}', None)
                self.assertEqual(set_func_call_prov_attr.call_count, 2*i)
                args = set_func_call_prov_attr.call_args.args
                self.assertTupleEqual(args, (f'fchash_{i}', 'next_revalidation', i))
            get_func_call_prov_attr.assert_not_called()

if __name__ == '__main__':
    unittest.main()