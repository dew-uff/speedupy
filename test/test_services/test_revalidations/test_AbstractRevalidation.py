import unittest, os, sys
from unittest.mock import patch

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from services.revalidations.AbstractRevalidation import AbstractRevalidation

class TestAbstractRevalidation(unittest.TestCase):
    def setUp(self):
        self.abstractRevalidation = AbstractRevalidation()
        self.get_func_call_prov_attr_namespace = 'services.revalidations.AbstractRevalidation.get_func_call_prov_attr'
        self.set_func_call_prov_attr_namespace = 'services.revalidations.AbstractRevalidation.set_func_call_prov_attr'
    
    def test_revalidation_in_current_execution_when_revalidation_will_occur(self):
        with patch(self.get_func_call_prov_attr_namespace, return_value=0) as get_func_call_prov_attr:
            reval_exec = self.abstractRevalidation.revalidation_in_current_execution('func_call_hash')
            self.assertTrue(reval_exec)
            get_func_call_prov_attr.assert_called_once()
    
    def test_revalidation_in_current_execution_when_revalidation_will_not_occur(self):
        with patch(self.get_func_call_prov_attr_namespace, return_value=3) as get_func_call_prov_attr:
            reval_exec = self.abstractRevalidation.revalidation_in_current_execution('func_call_hash')
            self.assertFalse(reval_exec)
            get_func_call_prov_attr.assert_called_once()
    
    def test_decrement_num_exec_to_next_revalidation_when_common_decrement(self):
        with patch(self.get_func_call_prov_attr_namespace, return_value=3) as get_func_call_prov_attr, \
             patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            self.abstractRevalidation.decrement_num_exec_to_next_revalidation('func_call_hash')
            get_func_call_prov_attr.assert_called_once()
            set_func_call_prov_attr.assert_called_once()
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('func_call_hash', 'next_revalidation', 2))

    def test_decrement_num_exec_to_next_revalidation_when_decrement_to_0(self):
        with patch(self.get_func_call_prov_attr_namespace, return_value=1) as get_func_call_prov_attr, \
             patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            self.abstractRevalidation.decrement_num_exec_to_next_revalidation('func_call_hash')
            get_func_call_prov_attr.assert_called_once()
            set_func_call_prov_attr.assert_called_once()
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('func_call_hash', 'next_revalidation', 0))
    
    def test_set_next_revalidation_with_greater_number_without_force(self):
        with patch(self.get_func_call_prov_attr_namespace, return_value=3) as get_func_call_prov_attr, \
             patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            self.abstractRevalidation.set_next_revalidation(10, 'func_call_hash', force=False)
            get_func_call_prov_attr.assert_called_once()
            set_func_call_prov_attr.assert_not_called()

    def test_set_next_revalidation_with_lower_number_without_force(self):
        with patch(self.get_func_call_prov_attr_namespace, return_value=9) as get_func_call_prov_attr, \
             patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            self.abstractRevalidation.set_next_revalidation(2, 'func_call_hash', force=False)
            get_func_call_prov_attr.assert_called_once()
            set_func_call_prov_attr.assert_called_once()
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('func_call_hash', 'next_revalidation', 2))

    def test_set_next_revalidation_with_equal_number(self):
        with patch(self.get_func_call_prov_attr_namespace, return_value=6) as get_func_call_prov_attr, \
             patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            self.abstractRevalidation.set_next_revalidation(6, 'func_call_hash', force=False)
            get_func_call_prov_attr.assert_called_once()
            set_func_call_prov_attr.assert_not_called()

    def test_set_next_revalidation_with_greater_number_with_force(self):
        with patch(self.get_func_call_prov_attr_namespace, return_value=6) as get_func_call_prov_attr, \
             patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            self.abstractRevalidation.set_next_revalidation(12, 'func_call_hash', force=True)
            get_func_call_prov_attr.assert_not_called()
            set_func_call_prov_attr.assert_called_once()
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('func_call_hash', 'next_revalidation', 12))

    def test_set_next_revalidation_with_lower_number_with_force(self):
        with patch(self.get_func_call_prov_attr_namespace, return_value=6) as get_func_call_prov_attr, \
             patch(self.set_func_call_prov_attr_namespace) as set_func_call_prov_attr:
            self.abstractRevalidation.set_next_revalidation(2, 'func_call_hash', force=True)
            get_func_call_prov_attr.assert_not_called()
            set_func_call_prov_attr.assert_called_once()
            args = set_func_call_prov_attr.call_args.args
            self.assertTupleEqual(args, ('func_call_hash', 'next_revalidation', 2))
    
if __name__ == '__main__':
    unittest.main()