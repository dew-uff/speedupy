import unittest, os, sys
from unittest.mock import patch
from pickle import dumps

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.execution_modes.ProbabilisticCountingMode import ProbabilisticCountingMode
from execute_exp.entitites.FunctionCallProv import FunctionCallProv
from execute_exp.entitites.Metadata import Metadata

class TestProbabilisticCountingMode(unittest.TestCase):
    def setUp(self):
        self.countingMode = ProbabilisticCountingMode(10, 10)
        self.fc_prov = FunctionCallProv(None, None, None, None, None, None, None, None, None, None, None, None, None)
        self.get_function_call_prov_entry_namespace = 'execute_exp.services.execution_modes.ProbabilisticCountingMode.DataAccess.get_function_call_prov_entry'
    
    def test_get_func_call_cache_with_different_output_types(self):
        self.fc_prov.mode_output = 12
        self.assertEqual(self.countingMode.get_func_call_cache(self.fc_prov), 12)
        
        self.fc_prov.mode_output = 'my_result'
        self.assertEqual(self.countingMode.get_func_call_cache(self.fc_prov), 'my_result')
        
        self.fc_prov.mode_output = [1, 4, 3]
        self.assertEqual(self.countingMode.get_func_call_cache(self.fc_prov), [1, 4, 3])
        
        self.fc_prov.mode_output = {1, True, 'xyz'}
        self.assertEqual(self.countingMode.get_func_call_cache(self.fc_prov), {1, True, 'xyz'})
        
        self.fc_prov.mode_output = MyClass()
        self.assertEqual(dumps(self.countingMode.get_func_call_cache(self.fc_prov)),
                         dumps(MyClass()))

    def test_func_call_acted_as_expected_when_metadata_returned_the_statistical_mode(self):
        metadata = Metadata('func_call_hash', [], {}, True, 0)
        self.fc_prov.mode_output = True
        self.assertTrue(self.countingMode.func_call_acted_as_expected(self.fc_prov, metadata))

    def test_func_call_acted_as_expected_when_metadata_did_not_return_the_statistical_mode(self):
        metadata = Metadata('func_call_hash', [], {}, 1.5, 0)
        self.fc_prov.mode_output = 1
        self.assertFalse(self.countingMode.func_call_acted_as_expected(self.fc_prov, metadata))

    def test_func_call_acted_as_expected_when_function_acted_as_expected_with_different_data_types(self):
        metadata = Metadata('func_call_hash', [], {}, [{True:10}, {False:-2}], 0)
        self.fc_prov.mode_output = [{True:10}, {False:-2}]
        self.assertTrue(self.countingMode.func_call_acted_as_expected(self.fc_prov, metadata))

        metadata = Metadata('func_call_hash', [], {}, {1, 4, 'test', 7, MyClass()}, 0)
        self.fc_prov.mode_output = {1, 4, 'test', 7, MyClass()}
        self.assertTrue(self.countingMode.func_call_acted_as_expected(self.fc_prov, metadata))

        metadata = Metadata('func_call_hash', [], {}, MyClass(), 0)
        self.fc_prov.mode_output = MyClass()
        self.assertTrue(self.countingMode.func_call_acted_as_expected(self.fc_prov, metadata))

        metadata = Metadata('func_call_hash', [], {}, (1, {2:False}, False, 7.123), 0)
        self.fc_prov.mode_output = (1, {2:False}, False, 7.123)
        self.assertTrue(self.countingMode.func_call_acted_as_expected(self.fc_prov, metadata))

class MyClass():
    def __init__(self):
        self.__x = 10
        self.__y = 20

if __name__ == '__main__':
    unittest.main()