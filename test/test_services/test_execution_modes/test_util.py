import unittest, os, sys
from unittest.mock import patch
from pickle import dumps

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from services.execution_modes.util import func_call_mode_output_occurs_enough, _set_statistical_mode_helpers, function_outputs_dict_2_array
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
        self.function_call_prov._FunctionCallProv__outputs = {dumps(10): 5}
        self.function_call_prov.total_num_exec = 5
        self.function_call_prov.mode_output = None
        self.function_call_prov.mode_rel_freq = None
        _set_statistical_mode_helpers(self.function_call_prov)
        self.assertEqual(self.function_call_prov.mode_output, 10)
        self.assertEqual(self.function_call_prov.mode_rel_freq, 1)

    def test_set_statistical_mode_helpers_when_has_many_outputs(self):
        self.function_call_prov._FunctionCallProv__outputs = {dumps(10): 5,
                                                              dumps(6.123): 10,
                                                              dumps(1): 5,
                                                              dumps(-2): 300}
        self.function_call_prov.total_num_exec = 320
        self.function_call_prov.mode_output = None
        self.function_call_prov.mode_rel_freq = None
        _set_statistical_mode_helpers(self.function_call_prov)
        self.assertEqual(self.function_call_prov.mode_output, -2)
        self.assertEqual(self.function_call_prov.mode_rel_freq, 0.9375)

    def test_set_statistical_mode_helpers_when_has_two_modes(self):
        self.function_call_prov._FunctionCallProv__outputs = {dumps(10): 5,
                                                              dumps(6.123): 30,
                                                              dumps(1): 5,
                                                              dumps(-2): 30}
        self.function_call_prov.total_num_exec = 70
        self.function_call_prov.mode_output = None
        self.function_call_prov.mode_rel_freq = None
        _set_statistical_mode_helpers(self.function_call_prov)
        self.assertEqual(self.function_call_prov.mode_output, 6.123)
        self.assertEqual(round(self.function_call_prov.mode_rel_freq, 9), 0.428571429)

    def test_function_output_dicts_2_array_when_func_has_one_output_with_freq_one(self):
        func_outputs = {dumps(10): 1}
        array = function_outputs_dict_2_array(func_outputs)
        self.assertListEqual(array, [10])

    def test_function_output_dicts_2_array_when_func_has_one_output_with_freq_greather_than_one(self):
        func_outputs = {dumps(1.23): 5}
        array = function_outputs_dict_2_array(func_outputs)
        self.assertListEqual(array, [1.23, 1.23, 1.23, 1.23, 1.23])
        
    def test_function_output_dicts_2_array_when_func_has_many_outputs(self):
        func_outputs = {dumps(1.23): 2,
                        dumps(-4.76): 5,
                        dumps(223.6): 10}
        array = function_outputs_dict_2_array(func_outputs)
        self.assertListEqual(array, [1.23, 1.23] + 5*[-4.76] + 10*[223.6])

if __name__ == '__main__':
    unittest.main()