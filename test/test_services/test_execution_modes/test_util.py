import unittest, os, sys
from unittest.mock import patch

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from services.execution_modes.util import func_call_mode_output_occurs_enough, _set_statistical_mode_helpers
from entities.FunctionCallProv import FunctionCallProv

class TestUtil(unittest.TestCase):
    def setUp(self):
        self.function_call_prov = FunctionCallProv(None, None, None, None, None, None, None, None, None, None, None, None, None)
        self.get_func_call_prov_namespace = 'services.execution_modes.util.get_func_call_prov'

    def test_func_call_mode_output_occurs_enough_when_function_occurs_more_than_necessary(self):
        self.function_call_prov.mode_rel_freq = 0.8
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(func_call_mode_output_occurs_enough('func_call_hash', 0.5))
            get_func_call_prov.assert_called_once()

    def test_func_call_mode_output_occurs_enough_when_function_occurs_exactly_the_necessary_percentage(self):
        self.function_call_prov.mode_rel_freq = 0.7
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(func_call_mode_output_occurs_enough('func_call_hash', 0.7))
            get_func_call_prov.assert_called_once()

    def test_func_call_mode_output_occurs_enough_when_function_occurs_less_than_necessary(self):
        self.function_call_prov.mode_rel_freq = 0.1
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertFalse(func_call_mode_output_occurs_enough('func_call_hash', 0.6))
            get_func_call_prov.assert_called_once()

    def test_set_statistical_mode_helpers_when_has_one_output(self):
        self.function_call_prov._FunctionCallProv__outputs = [{'value': 10, 'freq': 5}]
        self.function_call_prov.total_num_exec = 5
        self.function_call_prov.mode_output = None
        self.function_call_prov.mode_rel_freq = None
        _set_statistical_mode_helpers(self.function_call_prov)
        self.assertEqual(self.function_call_prov.mode_output, 10)
        self.assertEqual(self.function_call_prov.mode_rel_freq, 1)

    def test_set_statistical_mode_helpers_when_has_many_outputs(self):
        self.function_call_prov._FunctionCallProv__outputs = [{'value': 10, 'freq': 5},
                                                              {'value': 6.123, 'freq': 10},
                                                              {'value': 1, 'freq': 5},
                                                              {'value': -2, 'freq': 300}]
        self.function_call_prov.total_num_exec = 320
        self.function_call_prov.mode_output = None
        self.function_call_prov.mode_rel_freq = None
        _set_statistical_mode_helpers(self.function_call_prov)
        self.assertEqual(self.function_call_prov.mode_output, -2)
        self.assertEqual(self.function_call_prov.mode_rel_freq, 0.9375)

    def test_set_statistical_mode_helpers_when_has_two_modes(self):
        self.function_call_prov._FunctionCallProv__outputs = [{'value': 10, 'freq': 5},
                                                              {'value': 6.123, 'freq': 30},
                                                              {'value': 1, 'freq': 5},
                                                              {'value': -2, 'freq': 30}]
        self.function_call_prov.total_num_exec = 70
        self.function_call_prov.mode_output = None
        self.function_call_prov.mode_rel_freq = None
        _set_statistical_mode_helpers(self.function_call_prov)
        self.assertEqual(self.function_call_prov.mode_output, 6.123)
        self.assertEqual(round(self.function_call_prov.mode_rel_freq, 9), 0.428571429)

if __name__ == '__main__':
    unittest.main()