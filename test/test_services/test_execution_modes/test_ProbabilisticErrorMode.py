import unittest, os, sys, io
from unittest.mock import patch
import scipy.stats as st
from pickle import dumps

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from services.execution_modes.ProbabilisticErrorMode import ProbabilisticErrorMode
from entities.FunctionCallProv import FunctionCallProv
from constantes import Constantes

class TestProbabilisticErrorMode(unittest.TestCase):
    def setUp(self):
        self.errorMode = ProbabilisticErrorMode()
        self.function_call_prov = FunctionCallProv(None, None, None, None, None, None, None, None, None, None, None, None, None)
        self.get_func_call_prov_namespace = 'services.execution_modes.ProbabilisticErrorMode.get_func_call_prov'
        self.set_necessary_helpers_namespace = 'services.execution_modes.ProbabilisticErrorMode.ProbabilisticErrorMode._set_necessary_helpers'
        self.function_outputs_dict_2_array_namespace = 'services.execution_modes.ProbabilisticErrorMode.function_outputs_dict_2_array'
    
    def test_func_call_can_be_cached_when_function_error_helper_is_none_and_user_set_max_error_per_function(self):
        def set_confidence_error():
            self.errorMode._ProbabilisticErrorMode__func_call_prov.confidence_error = 0.1
        
        self.function_call_prov.confidence_error = None
        self.function_call_prov.confidence_lv = None
        Constantes().g_argsp_max_error_per_function = 0.2
        Constantes().g_argsp_confidence_level = 0.95
        with patch(self.set_necessary_helpers_namespace, side_effect=set_confidence_error) as set_necessary_helpers, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_called_once()

    def test_func_call_can_be_cached_when_function_error_helper_is_none_and_user_does_not_set_max_error_per_function(self):
        self.function_call_prov.confidence_error = None
        self.function_call_prov.confidence_lv = None
        Constantes().g_argsp_max_error_per_function = None
        Constantes().g_argsp_confidence_level = 0.95
        with patch(self.set_necessary_helpers_namespace) as set_necessary_helpers, \
             patch(self.get_func_call_prov_namespace) as get_func_call_prov:
            self.assertTrue(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_not_called()
            set_necessary_helpers.assert_not_called()

    def test_func_call_can_be_cached_when_function_error_helper_is_calculated_with_a_different_confidence_level(self):
        def set_confidence_error():
            self.errorMode._ProbabilisticErrorMode__func_call_prov.confidence_error = 0.1
        
        self.function_call_prov.confidence_error = 0.6
        self.function_call_prov.confidence_lv = 0.99
        Constantes().g_argsp_max_error_per_function = 0.2
        Constantes().g_argsp_confidence_level = 0.95
        with patch(self.set_necessary_helpers_namespace, side_effect=set_confidence_error) as set_necessary_helpers, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_called_once()

    def test_func_call_can_be_cached_when_function_error_helper_is_calculated_with_the_same_confidence_level(self):
        self.function_call_prov.confidence_error = 0.3
        self.function_call_prov.confidence_lv = 0.95
        Constantes().g_argsp_max_error_per_function = 0.2
        Constantes().g_argsp_confidence_level = 0.95
        with patch(self.set_necessary_helpers_namespace) as set_necessary_helpers, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertFalse(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_not_called()

    def test_func_call_can_be_cached_when_func_error_is_greater_than_user_max_error_per_function(self):
        self.function_call_prov.confidence_error = 0.5
        self.function_call_prov.confidence_lv = 0.95
        Constantes().g_argsp_max_error_per_function = 0.2
        Constantes().g_argsp_confidence_level = 0.95
        with patch(self.set_necessary_helpers_namespace) as set_necessary_helpers, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertFalse(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_not_called()

    def test_func_call_can_be_cached_when_func_error_is_equal_to_the_user_max_error_per_function(self):
        self.function_call_prov.confidence_error = 0.213
        self.function_call_prov.confidence_lv = 0.95
        Constantes().g_argsp_max_error_per_function = 0.213
        Constantes().g_argsp_confidence_level = 0.95
        with patch(self.set_necessary_helpers_namespace) as set_necessary_helpers, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_not_called()

    def test_func_call_can_be_cached_when_func_error_is_lower_than_the_user_max_error_per_function(self):
        self.function_call_prov.confidence_error = 0.112312
        self.function_call_prov.confidence_lv = 0.95
        Constantes().g_argsp_max_error_per_function = 0.2412
        Constantes().g_argsp_confidence_level = 0.95
        with patch(self.set_necessary_helpers_namespace) as set_necessary_helpers, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_not_called()

    @patch('sys.stderr', new_callable=io.StringIO)
    def test_set_necessary_helpers_when_function_has_one_output_value(self, stderr_mock):
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = {dumps(2): 10}
        self.function_call_prov.total_num_exec = 10
        Constantes().g_argsp_confidence_level = 0.95
        with patch(self.function_outputs_dict_2_array_namespace, return_value=10*[2]) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.function_call_prov.mean_output, 2)
            self.assertEqual(self.function_call_prov.confidence_lv, 0.95)
            self.assertEqual(self.function_call_prov.confidence_low_limit, 2)
            self.assertEqual(self.function_call_prov.confidence_up_limit, 2)
            self.assertEqual(self.function_call_prov.confidence_error, 0)

    def test_set_necessary_helpers_when_function_has_many_output_values(self):
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = {dumps(2): 10,
                                                              dumps(0): 3,
                                                              dumps(-1.3): 6,
                                                              dumps(4.27): 8}
        self.function_call_prov.total_num_exec = 27
        Constantes().g_argsp_confidence_level = 0.99
        output_array = 10*[2] + 3*[0] + 6*[-1.3] + 8*[4.27]
        output_mean = st.tmean(output_array)
        interval = st.t.interval(0.99, 26, loc=output_mean, scale=st.sem(output_array))
        output_error = round((interval[1] - interval[0])/2, 9)
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.function_call_prov.mean_output, output_mean)
            self.assertEqual(self.function_call_prov.confidence_lv, 0.99)
            self.assertEqual(self.function_call_prov.confidence_low_limit, interval[0])
            self.assertEqual(self.function_call_prov.confidence_up_limit, interval[1])
            self.assertEqual(round(self.function_call_prov.confidence_error, 9), output_error)

    def test_set_necessary_helpers_when_function_executed_less_than_30_times(self):
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = {dumps(2): 10,
                                                              dumps(0): 5,
                                                              dumps(4.27): 8}
        self.function_call_prov.total_num_exec = 23
        Constantes().g_argsp_confidence_level = 0.77
        output_array = 10*[2] + 5*[0] + 8*[4.27]
        output_mean = st.tmean(output_array)
        interval = st.t.interval(0.77, 22, loc=output_mean, scale=st.sem(output_array))
        output_error = round((interval[1] - interval[0])/2, 9)
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.function_call_prov.mean_output, output_mean)
            self.assertEqual(self.function_call_prov.confidence_lv, 0.77)
            self.assertEqual(self.function_call_prov.confidence_low_limit, interval[0])
            self.assertEqual(self.function_call_prov.confidence_up_limit, interval[1])
            self.assertEqual(round(self.function_call_prov.confidence_error, 9), output_error)

    def test_set_necessary_helpers_when_function_executed_exactly_30_times(self):
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = {dumps(2): 10,
                                                              dumps(3): 8,
                                                              dumps(-2.01): 12}
        self.function_call_prov.total_num_exec = 30
        Constantes().g_argsp_confidence_level = 0.88
        output_array = 10*[2] + 8*[3] + 12*[-2.01]
        output_mean = st.tmean(output_array)
        interval = st.t.interval(0.88, 29, loc=output_mean, scale=st.sem(output_array))
        output_error = round((interval[1] - interval[0])/2, 9)
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.function_call_prov.mean_output, output_mean)
            self.assertEqual(self.function_call_prov.confidence_lv, 0.88)
            self.assertEqual(self.function_call_prov.confidence_low_limit, interval[0])
            self.assertEqual(self.function_call_prov.confidence_up_limit, interval[1])
            self.assertEqual(round(self.function_call_prov.confidence_error, 9), output_error)

    def test_set_necessary_helpers_when_function_executed_exactly_31_times(self):
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = {dumps(2): 10,
                                                              dumps(3): 9,
                                                              dumps(-2.01): 12}
        self.function_call_prov.total_num_exec = 31
        Constantes().g_argsp_confidence_level = 0.66
        output_array = 10*[2] + 9*[3] + 12*[-2.01]
        output_mean = st.tmean(output_array)
        interval = st.norm.interval(0.66, loc=output_mean, scale=st.sem(output_array))
        output_error = round((interval[1] - interval[0])/2, 9)
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.function_call_prov.mean_output, output_mean)
            self.assertEqual(self.function_call_prov.confidence_lv, 0.66)
            self.assertEqual(self.function_call_prov.confidence_low_limit, interval[0])
            self.assertEqual(self.function_call_prov.confidence_up_limit, interval[1])
            self.assertEqual(round(self.function_call_prov.confidence_error, 9), output_error)

    def test_set_necessary_helpers_when_function_executed_more_than_30_times(self):
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = {dumps(-5.2): 30,
                                                              dumps(-4): 10,
                                                              dumps(-7.01): 12}
        self.function_call_prov.total_num_exec = 52
        Constantes().g_argsp_confidence_level = 0.8
        output_array = 30*[-5.2] + 10*[-4] + 12*[-7.01]
        output_mean = st.tmean(output_array)
        interval = st.norm.interval(0.8, loc=output_mean, scale=st.sem(output_array))
        output_error = round((interval[1] - interval[0])/2, 9)
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.function_call_prov.mean_output, output_mean)
            self.assertEqual(self.function_call_prov.confidence_lv, 0.8)
            self.assertEqual(self.function_call_prov.confidence_low_limit, interval[0])
            self.assertEqual(self.function_call_prov.confidence_up_limit, interval[1])
            self.assertEqual(round(self.function_call_prov.confidence_error, 9), output_error)

    def test_get_func_call_cache_when_func_mean_output_helper_is_None(self):
        self.function_call_prov.mean_output = None
        output_array = 5*[3] + 2*[0]
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(round(self.errorMode.get_func_call_cache('func_call_hash'), 9),
                             round(st.tmean(output_array), 9))
            get_func_call_prov.assert_called_once()
            function_outputs_dict_2_array.assert_called_once()

    def test_get_func_call_cache_when_func_mean_output_helper_is_not_None(self):
        self.function_call_prov.mean_output = 0.23
        with patch(self.function_outputs_dict_2_array_namespace) as function_outputs_dict_2_array, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.errorMode.get_func_call_cache('func_call_hash'), 0.23)
            get_func_call_prov.assert_called_once()
            function_outputs_dict_2_array.assert_not_called()

if __name__ == '__main__':
    unittest.main()