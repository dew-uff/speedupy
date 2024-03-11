import unittest, os, sys
from unittest.mock import patch
from pickle import dumps

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.execution_modes.ProbabilisticCountingMode import ProbabilisticCountingMode
from entities.FunctionCallProv import FunctionCallProv
from entities.Metadata import Metadata

class TestProbabilisticCountingMode(unittest.TestCase):
    def setUp(self):
        self.countingMode = ProbabilisticCountingMode()
        self.function_call_prov = FunctionCallProv(None, None, None, None, None, None, None, None, None, None, None, None, None)
        self.get_function_call_prov_entry_namespace = 'execute_exp.services.execution_modes.ProbabilisticCountingMode.get_function_call_prov_entry'
    
    def test_get_func_call_cache_with_different_output_types(self):
        self.function_call_prov.mode_output = 12
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.countingMode.get_func_call_cache('func_call_hash'), 12)
            get_func_call_prov.assert_called_once()
        
        self.function_call_prov.mode_output = 'my_result'
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.countingMode.get_func_call_cache('func_call_hash'), 'my_result')
            get_func_call_prov.assert_called_once()

        self.function_call_prov.mode_output = [1, 4, 3]
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.countingMode.get_func_call_cache('func_call_hash'), [1, 4, 3])
            get_func_call_prov.assert_called_once()

        self.function_call_prov.mode_output = {1, True, 'xyz'}
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.countingMode.get_func_call_cache('func_call_hash'), {1, True, 'xyz'})
            get_func_call_prov.assert_called_once()

        self.function_call_prov.mode_output = MyClass()
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(dumps(self.countingMode.get_func_call_cache('func_call_hash')),
                             dumps(MyClass()))
            get_func_call_prov.assert_called_once()

    def test_func_call_acted_as_expected_when_metadata_returned_the_statistical_mode(self):
        metadata = Metadata('func_call_hash', [], {}, True, 0)
        self.function_call_prov.mode_output = True
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(self.countingMode.func_call_acted_as_expected('func_call_hash', metadata))
            get_func_call_prov.assert_called_once()

    def test_func_call_acted_as_expected_when_metadata_did_not_return_the_statistical_mode(self):
        metadata = Metadata('func_call_hash', [], {}, 1.5, 0)
        self.function_call_prov.mode_output = 1
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertFalse(self.countingMode.func_call_acted_as_expected('func_call_hash', metadata))
            get_func_call_prov.assert_called_once()

    def test_func_call_acted_as_expected_when_function_acted_as_expected_with_different_data_types(self):
        metadata = Metadata('func_call_hash', [], {}, [{True:10}, {False:-2}], 0)
        self.function_call_prov.mode_output = [{True:10}, {False:-2}]
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(self.countingMode.func_call_acted_as_expected('func_call_hash', metadata))
            get_func_call_prov.assert_called_once()

        metadata = Metadata('func_call_hash', [], {}, {1, 4, 'test', 7, MyClass()}, 0)
        self.function_call_prov.mode_output = {1, 4, 'test', 7, MyClass()}
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(self.countingMode.func_call_acted_as_expected('func_call_hash', metadata))
            get_func_call_prov.assert_called_once()

        metadata = Metadata('func_call_hash', [], {}, MyClass(), 0)
        self.function_call_prov.mode_output = MyClass()
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(self.countingMode.func_call_acted_as_expected('func_call_hash', metadata))
            get_func_call_prov.assert_called_once()

        metadata = Metadata('func_call_hash', [], {}, (1, {2:False}, False, 7.123), 0)
        self.function_call_prov.mode_output = (1, {2:False}, False, 7.123)
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(self.countingMode.func_call_acted_as_expected('func_call_hash', metadata))
            get_func_call_prov.assert_called_once()

class MyClass():
    def __init__(self):
        self.__x = 10
        self.__y = 20

if __name__ == '__main__':
    unittest.main()