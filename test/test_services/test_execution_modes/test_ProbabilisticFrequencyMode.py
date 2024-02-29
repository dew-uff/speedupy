import unittest, os, sys, io, pickle
from unittest.mock import patch
import scipy.stats as st

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from services.execution_modes.ProbabilisticFrequencyMode import ProbabilisticFrequencyMode
from entities.FunctionCallProv import FunctionCallProv
from constantes import Constantes

class TestProbabilisticFrequencyMode(unittest.TestCase):
    def setUp(self):
        self.frequencyMode = ProbabilisticFrequencyMode()
        self.function_call_prov = FunctionCallProv(None, None, None, None, None, None, None, None, None, None, None, None, None)
        self.get_func_call_prov_namespace = 'services.execution_modes.ProbabilisticFrequencyMode.get_func_call_prov'
        self.calculate_weighted_output_seq_namespace = 'services.execution_modes.ProbabilisticFrequencyMode.ProbabilisticFrequencyMode._calculate_weighted_output_seq'

    def test_get_func_call_cache_when_function_weighted_seq_helper_is_None(self):
        def set_weighted_output_seq():
            self.function_call_prov.weighted_output_seq = [2, 4, 6, 8, 10]
        
        self.function_call_prov.next_index_weighted_seq = 0
        self.function_call_prov.weighted_output_seq = None
        with patch(self.calculate_weighted_output_seq_namespace, side_effect=set_weighted_output_seq) as calculate_weighted_output_seq, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 2)
            self.assertEqual(get_func_call_prov.call_count, 1)
            calculate_weighted_output_seq.assert_called_once()

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 4)
            self.assertEqual(get_func_call_prov.call_count, 2)

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 6)
            self.assertEqual(get_func_call_prov.call_count, 3)

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 8)
            self.assertEqual(get_func_call_prov.call_count, 4)

            calculate_weighted_output_seq.assert_called_once()

    def test_get_func_call_cache_when_function_weighted_seq_helper_is_not_None(self):
        self.function_call_prov.next_index_weighted_seq = 0
        self.function_call_prov.weighted_output_seq = [3, False, 2.45, 'teste']
        with patch(self.calculate_weighted_output_seq_namespace) as calculate_weighted_output_seq, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 3)
            self.assertEqual(get_func_call_prov.call_count, 1)

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), False)
            self.assertEqual(get_func_call_prov.call_count, 2)

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 2.45)
            self.assertEqual(get_func_call_prov.call_count, 3)

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 'teste')
            self.assertEqual(get_func_call_prov.call_count, 4)

            calculate_weighted_output_seq.assert_not_called()

    def test_get_func_call_cache_when_third_result_of_weighted_seq_should_be_returned(self):
        self.function_call_prov.next_index_weighted_seq = 2
        self.function_call_prov.weighted_output_seq = [3, False, 2.45, 'teste']
        with patch(self.calculate_weighted_output_seq_namespace) as calculate_weighted_output_seq, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 2.45)
            self.assertEqual(get_func_call_prov.call_count, 1)

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 'teste')
            self.assertEqual(get_func_call_prov.call_count, 2)

            calculate_weighted_output_seq.assert_not_called()

    def test_get_func_call_cache_called_multiple_times_til_the_end_of_the_seq_and_restarting_it(self):
        self.function_call_prov.next_index_weighted_seq = 0
        self.function_call_prov.weighted_output_seq = [0.094, False, 'teste']
        with patch(self.calculate_weighted_output_seq_namespace) as calculate_weighted_output_seq, \
             patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 0.094)
            self.assertEqual(get_func_call_prov.call_count, 1)

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), False)
            self.assertEqual(get_func_call_prov.call_count, 2)

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'),  'teste')
            self.assertEqual(get_func_call_prov.call_count, 3)

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), 0.094)
            self.assertEqual(get_func_call_prov.call_count, 4)

            self.assertEqual(self.frequencyMode.get_func_call_cache('func_call_hash'), False)
            self.assertEqual(get_func_call_prov.call_count, 5)

            calculate_weighted_output_seq.assert_not_called()
    
    def test_calculate_weighted_output_seq_when_function_has_only_one_output_values(self):
        self.frequencyMode._ProbabilisticFrequencyMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = [{'value': 2, 'freq': 10}]
        self.function_call_prov.mode_output = 2
        
        self.frequencyMode._calculate_weighted_output_seq()
        self.assertListEqual(self.function_call_prov.weighted_output_seq, 10*[2])

    def test_calculate_weighted_output_seq_when_function_has_only_two_output_values(self):
        self.frequencyMode._ProbabilisticFrequencyMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = [{'value': 1, 'freq': 6},
                                                              {'value': 2, 'freq': 3},]
        self.function_call_prov.mode_output = 1
        
        self.frequencyMode._calculate_weighted_output_seq()
        self.assertListEqual(self.function_call_prov.weighted_output_seq, [1, 1, 2, 1, 1, 2, 1, 1, 2])
    
    def test_calculate_weighted_output_seq_when_function_has_many_output_values_and_the_division_by_the_mode_output_freq_is_a_non_integer_division(self):
        self.frequencyMode._ProbabilisticFrequencyMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = [{'value': 1, 'freq': 6},
                                                              {'value': 2, 'freq': 4},
                                                              {'value': 3, 'freq': 3}]
        self.function_call_prov.mode_output = 1
        
        self.frequencyMode._calculate_weighted_output_seq()
        self.assertListEqual(self.function_call_prov.weighted_output_seq, [1, 1, 2, 3, 1, 1, 2, 3, 1, 1, 2, 3, 2])

    def test_calculate_weighted_output_seq_when_there_is_no_remaining_outputs_after_mode_is_completely_added_to_the_seq(self):
        self.frequencyMode._ProbabilisticFrequencyMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = [{'value': True, 'freq': 10},
                                                              {'value': 'my_teste', 'freq': 5},
                                                              {'value': -3.14, 'freq': 2}]
        self.function_call_prov.mode_output = True
        
        self.frequencyMode._calculate_weighted_output_seq()
        self.assertListEqual(self.function_call_prov.weighted_output_seq, [True, True, 'my_teste', True, True, 'my_teste', True, -3.14, True, 'my_teste', True, True, 'my_teste', True, True, 'my_teste', -3.14])

    def test_calculate_weighted_output_seq_when_there_is_one_remaining_output_after_mode_is_completely_added_to_the_seq(self):
        self.frequencyMode._ProbabilisticFrequencyMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = [{'value': False, 'freq': 6},
                                                              {'value': [1, 2, 3], 'freq': 3},
                                                              {'value': {1, 4, 2}, 'freq': 5}]
        self.function_call_prov.mode_output = False
        
        self.frequencyMode._calculate_weighted_output_seq()
        self.assertListEqual(self.function_call_prov.weighted_output_seq, [False, False, [1, 2, 3], {1, 4, 2}, False, False, [1, 2, 3], {1, 4, 2}, False, False, [1, 2, 3], {1, 4, 2}, {1, 4, 2}, {1, 4, 2}])
    
    def test_calculate_weighted_output_seq_when_there_are_many_remaining_output_after_mode_is_completely_added_to_the_seq(self):
        self.frequencyMode._ProbabilisticFrequencyMode__func_call_prov = self.function_call_prov
        self.function_call_prov._FunctionCallProv__outputs = [{'value': 2.23121, 'freq': 7},
                                                              {'value': (1, 2, 3), 'freq': 5},
                                                              {'value': MyClass(), 'freq': 6}]
        self.function_call_prov.mode_output = 2.23121
        
        self.frequencyMode._calculate_weighted_output_seq()
        expected_seq = [2.23121, 2.23121, (1, 2, 3), MyClass(),
                        2.23121, 2.23121, (1, 2, 3), MyClass(),
                        2.23121, 2.23121, (1, 2, 3), MyClass(),
                        2.23121, (1, 2, 3), MyClass(),
                        (1, 2, 3), MyClass(),
                        MyClass()]
        for i in range(len(expected_seq)):
            self.assertEqual(pickle.dumps(self.function_call_prov.weighted_output_seq[i]),
                             pickle.dumps(expected_seq[i]))

class MyClass():
    def __init__(self):
        self.__x = 1
        self.__y = 2

if __name__ == '__main__':
    unittest.main()