import unittest, os, sys, io
from unittest.mock import patch
import scipy.stats as st
from pickle import dumps

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.entitites.Metadata import Metadata
from execute_exp.entitites.FunctionCallProv import FunctionCallProv
from execute_exp.services.execution_modes.ProbabilisticErrorMode import ProbabilisticErrorMode

class TestProbabilisticErrorMode(unittest.TestCase):
    def setUp(self):
        self.errorMode = ProbabilisticErrorMode(10, 1, 0.95)
        self.fc_prov = FunctionCallProv(None, None, None, None, None, None, None, None, None, None, None, None, None)
        self.get_function_call_prov_entry_namespace = 'execute_exp.services.execution_modes.ProbabilisticErrorMode.DataAccess.get_function_call_prov_entry'
        self.set_necessary_helpers_namespace = 'execute_exp.services.execution_modes.ProbabilisticErrorMode.ProbabilisticErrorMode._set_necessary_helpers'
        self.function_outputs_dict_2_array_namespace = 'execute_exp.services.execution_modes.ProbabilisticErrorMode.function_outputs_dict_2_array'
    
    def test_func_call_can_be_cached_when_function_error_helper_is_none_and_user_set_max_error_per_function(self):
        def set_confidence_error():
            self.errorMode._ProbabilisticErrorMode__func_call_prov.confidence_error = 0.1
        
        self.errorMode = ProbabilisticErrorMode(10, 0.2, 0.95)
        self.fc_prov.confidence_error = None
        self.fc_prov.confidence_lv = None
        with patch(self.set_necessary_helpers_namespace, side_effect=set_confidence_error) as set_necessary_helpers, \
             patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertTrue(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_called_once()

    def test_func_call_can_be_cached_when_function_error_helper_is_none_and_user_does_not_set_max_error_per_function(self):
        self.errorMode = ProbabilisticErrorMode(10, None, 0.95)
        self.fc_prov.confidence_error = None
        self.fc_prov.confidence_lv = None
        with patch(self.set_necessary_helpers_namespace) as set_necessary_helpers, \
             patch(self.get_function_call_prov_entry_namespace) as get_func_call_prov:
            self.assertTrue(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_not_called()
            set_necessary_helpers.assert_not_called()

    def test_func_call_can_be_cached_when_function_error_helper_is_calculated_with_a_different_confidence_level(self):
        def set_confidence_error():
            self.errorMode._ProbabilisticErrorMode__func_call_prov.confidence_error = 0.1
        
        self.errorMode = ProbabilisticErrorMode(10, 0.2, 0.95)
        self.fc_prov.confidence_error = 0.6
        self.fc_prov.confidence_lv = 0.99
        with patch(self.set_necessary_helpers_namespace, side_effect=set_confidence_error) as set_necessary_helpers, \
             patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertTrue(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_called_once()

    def test_func_call_can_be_cached_when_function_error_helper_is_calculated_with_the_same_confidence_level(self):
        self.errorMode = ProbabilisticErrorMode(10, 0.2, 0.95)
        self.fc_prov.confidence_error = 0.3
        self.fc_prov.confidence_lv = 0.95
        with patch(self.set_necessary_helpers_namespace) as set_necessary_helpers, \
             patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertFalse(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_not_called()

    def test_func_call_can_be_cached_when_func_error_is_greater_than_user_max_error_per_function(self):
        self.errorMode = ProbabilisticErrorMode(10, 0.2, 0.95)
        self.fc_prov.confidence_error = 0.5
        self.fc_prov.confidence_lv = 0.95
        with patch(self.set_necessary_helpers_namespace) as set_necessary_helpers, \
             patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertFalse(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_not_called()

    def test_func_call_can_be_cached_when_func_error_is_equal_to_the_user_max_error_per_function(self):
        self.errorMode = ProbabilisticErrorMode(10, 0.213, 0.95)
        self.fc_prov.confidence_error = 0.213
        self.fc_prov.confidence_lv = 0.95
        with patch(self.set_necessary_helpers_namespace) as set_necessary_helpers, \
             patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertTrue(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_not_called()

    def test_func_call_can_be_cached_when_func_error_is_lower_than_the_user_max_error_per_function(self):
        self.errorMode = ProbabilisticErrorMode(10, 0.2412, 0.95)
        self.fc_prov.confidence_error = 0.112312
        self.fc_prov.confidence_lv = 0.95
        with patch(self.set_necessary_helpers_namespace) as set_necessary_helpers, \
             patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertTrue(self.errorMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
            set_necessary_helpers.assert_not_called()

    @patch('sys.stderr', new_callable=io.StringIO)
    def test_set_necessary_helpers_when_function_has_one_output_value(self, stderr_mock):
        self.errorMode = ProbabilisticErrorMode(10, 1, 0.95)
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.fc_prov
        self.fc_prov._FunctionCallProv__outputs = {dumps(2): 10}
        self.fc_prov.total_num_exec = 10
        with patch(self.function_outputs_dict_2_array_namespace, return_value=10*[2]) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.fc_prov.mean_output, 2)
            self.assertEqual(self.fc_prov.confidence_lv, 0.95)
            self.assertEqual(self.fc_prov.confidence_low_limit, 2)
            self.assertEqual(self.fc_prov.confidence_up_limit, 2)
            self.assertEqual(self.fc_prov.confidence_error, 0)

    def test_set_necessary_helpers_when_function_has_many_output_values(self):
        self.errorMode = ProbabilisticErrorMode(10, 1, 0.99)
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.fc_prov
        self.fc_prov._FunctionCallProv__outputs = {dumps(2): 10,
                                                              dumps(0): 3,
                                                              dumps(-1.3): 6,
                                                              dumps(4.27): 8}
        self.fc_prov.total_num_exec = 27
        output_array = 10*[2] + 3*[0] + 6*[-1.3] + 8*[4.27]
        output_mean = st.tmean(output_array)
        interval = st.t.interval(0.99, 26, loc=output_mean, scale=st.sem(output_array))
        output_error = round((interval[1] - interval[0])/2, 9)
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.fc_prov.mean_output, output_mean)
            self.assertEqual(self.fc_prov.confidence_lv, 0.99)
            self.assertEqual(self.fc_prov.confidence_low_limit, interval[0])
            self.assertEqual(self.fc_prov.confidence_up_limit, interval[1])
            self.assertEqual(round(self.fc_prov.confidence_error, 9), output_error)

    def test_set_necessary_helpers_when_function_executed_less_than_30_times(self):
        self.errorMode = ProbabilisticErrorMode(10, 1, 0.77)
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.fc_prov
        self.fc_prov._FunctionCallProv__outputs = {dumps(2): 10,
                                                              dumps(0): 5,
                                                              dumps(4.27): 8}
        self.fc_prov.total_num_exec = 23
        output_array = 10*[2] + 5*[0] + 8*[4.27]
        output_mean = st.tmean(output_array)
        interval = st.t.interval(0.77, 22, loc=output_mean, scale=st.sem(output_array))
        output_error = round((interval[1] - interval[0])/2, 9)
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.fc_prov.mean_output, output_mean)
            self.assertEqual(self.fc_prov.confidence_lv, 0.77)
            self.assertEqual(self.fc_prov.confidence_low_limit, interval[0])
            self.assertEqual(self.fc_prov.confidence_up_limit, interval[1])
            self.assertEqual(round(self.fc_prov.confidence_error, 9), output_error)

    def test_set_necessary_helpers_when_function_executed_exactly_30_times(self):
        self.errorMode = ProbabilisticErrorMode(10, 1, 0.88)
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.fc_prov
        self.fc_prov._FunctionCallProv__outputs = {dumps(2): 10,
                                                              dumps(3): 8,
                                                              dumps(-2.01): 12}
        self.fc_prov.total_num_exec = 30
        output_array = 10*[2] + 8*[3] + 12*[-2.01]
        output_mean = st.tmean(output_array)
        interval = st.t.interval(0.88, 29, loc=output_mean, scale=st.sem(output_array))
        output_error = round((interval[1] - interval[0])/2, 9)
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.fc_prov.mean_output, output_mean)
            self.assertEqual(self.fc_prov.confidence_lv, 0.88)
            self.assertEqual(self.fc_prov.confidence_low_limit, interval[0])
            self.assertEqual(self.fc_prov.confidence_up_limit, interval[1])
            self.assertEqual(round(self.fc_prov.confidence_error, 9), output_error)

    def test_set_necessary_helpers_when_function_executed_exactly_31_times(self):
        self.errorMode = ProbabilisticErrorMode(10, 1, 0.66)
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.fc_prov
        self.fc_prov._FunctionCallProv__outputs = {dumps(2): 10,
                                                              dumps(3): 9,
                                                              dumps(-2.01): 12}
        self.fc_prov.total_num_exec = 31
        output_array = 10*[2] + 9*[3] + 12*[-2.01]
        output_mean = st.tmean(output_array)
        interval = st.norm.interval(0.66, loc=output_mean, scale=st.sem(output_array))
        output_error = round((interval[1] - interval[0])/2, 9)
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.fc_prov.mean_output, output_mean)
            self.assertEqual(self.fc_prov.confidence_lv, 0.66)
            self.assertEqual(self.fc_prov.confidence_low_limit, interval[0])
            self.assertEqual(self.fc_prov.confidence_up_limit, interval[1])
            self.assertEqual(round(self.fc_prov.confidence_error, 9), output_error)

    def test_set_necessary_helpers_when_function_executed_more_than_30_times(self):
        self.errorMode = ProbabilisticErrorMode(10, 1, 0.8)
        self.errorMode._ProbabilisticErrorMode__func_call_prov = self.fc_prov
        self.fc_prov._FunctionCallProv__outputs = {dumps(-5.2): 30,
                                                              dumps(-4): 10,
                                                              dumps(-7.01): 12}
        self.fc_prov.total_num_exec = 52
        output_array = 30*[-5.2] + 10*[-4] + 12*[-7.01]
        output_mean = st.tmean(output_array)
        interval = st.norm.interval(0.8, loc=output_mean, scale=st.sem(output_array))
        output_error = round((interval[1] - interval[0])/2, 9)
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array:
            self.errorMode._set_necessary_helpers()
            function_outputs_dict_2_array.assert_called_once()
            self.assertEqual(self.fc_prov.mean_output, output_mean)
            self.assertEqual(self.fc_prov.confidence_lv, 0.8)
            self.assertEqual(self.fc_prov.confidence_low_limit, interval[0])
            self.assertEqual(self.fc_prov.confidence_up_limit, interval[1])
            self.assertEqual(round(self.fc_prov.confidence_error, 9), output_error)

    def test_get_func_call_cache_when_func_mean_output_helper_is_None(self):
        self.fc_prov.mean_output = None
        output_array = 5*[3] + 2*[0]
        with patch(self.function_outputs_dict_2_array_namespace, return_value=output_array) as function_outputs_dict_2_array, \
             patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertEqual(round(self.errorMode.get_func_call_cache('func_call_hash'), 9),
                             round(st.tmean(output_array), 9))
            get_func_call_prov.assert_called_once()
            function_outputs_dict_2_array.assert_called_once()

    def test_get_func_call_cache_when_func_mean_output_helper_is_not_None(self):
        self.fc_prov.mean_output = 0.23
        with patch(self.function_outputs_dict_2_array_namespace) as function_outputs_dict_2_array, \
             patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertEqual(self.errorMode.get_func_call_cache('func_call_hash'), 0.23)
            get_func_call_prov.assert_called_once()
            function_outputs_dict_2_array.assert_not_called()

    def test_func_call_acted_as_expected_when_metadata_returned_value_outside_the_expected_interval(self):
        metadata = Metadata('func_call_hash', [], {}, 9, 0)
        self.fc_prov.mean_output = 10
        self.fc_prov.confidence_error = 0.572
        self.assertFalse(self.errorMode.func_call_acted_as_expected(self.fc_prov, metadata))

    def test_func_call_acted_as_expected_when_metadata_returned_value_right_in_the_upper_limit_expected(self):
        metadata = Metadata('func_call_hash', [], {}, 10.152, 0)
        self.fc_prov.mean_output = 10
        self.fc_prov.confidence_error = 0.304
        self.assertTrue(self.errorMode.func_call_acted_as_expected(self.fc_prov, metadata))

    def test_func_call_acted_as_expected_when_metadata_returned_value_little_higher_than_the_upper_limit_expected(self):
        metadata = Metadata('func_call_hash', [], {}, 10.1521, 0)
        self.fc_prov.mean_output = 10
        self.fc_prov.confidence_error = 0.304
        self.assertFalse(self.errorMode.func_call_acted_as_expected(self.fc_prov, metadata))
        
    def test_func_call_acted_as_expected_when_metadata_returned_value_right_in_the_lower_limit_expected(self):
        metadata = Metadata('func_call_hash', [], {}, 2.889, 0)
        self.fc_prov.mean_output = 3
        self.fc_prov.confidence_error = 0.222
        self.assertTrue(self.errorMode.func_call_acted_as_expected(self.fc_prov, metadata))

    def test_func_call_acted_as_expected_when_metadata_returned_value_little_lower_than_the_lower_limit_expected(self):
        metadata = Metadata('func_call_hash', [], {}, 2.8889, 0)
        self.fc_prov.mean_output = 3
        self.fc_prov.confidence_error = 0.222
        self.assertFalse(self.errorMode.func_call_acted_as_expected(self.fc_prov, metadata))

    def test_func_call_acted_as_expected_when_metadata_returned_value_inside_the_expected_interval(self):
        metadata = Metadata('func_call_hash', [], {}, 3.1, 0)
        self.fc_prov.mean_output = 3
        self.fc_prov.confidence_error = 0.222
        self.assertTrue(self.errorMode.func_call_acted_as_expected(self.fc_prov, metadata))
        
    def test_func_call_acted_as_expected_when_metadata_returned_value_inside_the_confidence_interval_but_outside_the_expected_interval(self):
        metadata = Metadata('func_call_hash', [], {}, 3.2, 0)
        self.fc_prov.mean_output = 3
        self.fc_prov.confidence_error = 0.222
        self.assertFalse(self.errorMode.func_call_acted_as_expected(self.fc_prov, metadata))
        
    def test_func_call_acted_as_expected_when_metadata_returned_value_outside_the_confidence_interval(self):
        metadata = Metadata('func_call_hash', [], {}, 2, 0)
        self.fc_prov.mean_output = 3
        self.fc_prov.confidence_error = 0.222
        self.assertFalse(self.errorMode.func_call_acted_as_expected(self.fc_prov, metadata))

if __name__ == '__main__':
    unittest.main()