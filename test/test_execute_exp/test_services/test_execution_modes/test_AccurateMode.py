import unittest, os, sys
from pickle import dumps
from unittest.mock import patch

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.execution_modes.AccurateMode import AccurateMode
from execute_exp.entitites.FunctionCallProv import FunctionCallProv
from execute_exp.entitites.Metadata import Metadata

class TestAccurateMode(unittest.TestCase):
    def setUp(self):
        self.accurateMode = AccurateMode(10)
        self.fc_prov = FunctionCallProv(None, None, None, None, None, None, None, None, None, None, None, None, None)
        self.get_function_call_prov_entry_namespace = 'execute_exp.services.execution_modes.AccurateMode.DataAccess.get_function_call_prov_entry'
    
    def test_func_call_can_be_cached_when_func_has_one_output(self):
        self.fc_prov._FunctionCallProv__outputs = {dumps(1):12}
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertTrue(self.accurateMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
    
    def test_func_call_can_be_cached_when_func_has_2_outputs(self):
        self.fc_prov._FunctionCallProv__outputs = {dumps(2): 5,
                                                   dumps(3): 3}
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertFalse(self.accurateMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()

    def test_func_call_can_be_cached_when_func_has_many_outputs(self):
        self.fc_prov._FunctionCallProv__outputs = {dumps(1):12,
                                                   dumps(2):5,
                                                   dumps(3):3,
                                                   dumps(4):1}
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertFalse(self.accurateMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
    
    def test_get_func_call_cache_with_different_types(self):
        self.fc_prov._FunctionCallProv__outputs = {dumps(1):12}
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertEqual(self.accurateMode.get_func_call_cache('func_call_hash'), 1)
            get_func_call_prov.assert_called_once()

        self.fc_prov._FunctionCallProv__outputs = {dumps('my_result'):12}
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertEqual(self.accurateMode.get_func_call_cache('func_call_hash'), 'my_result')
            get_func_call_prov.assert_called_once()

        self.fc_prov._FunctionCallProv__outputs = {dumps({1, 2, 3}):12}
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertEqual(self.accurateMode.get_func_call_cache('func_call_hash'), {1, 2, 3})
            get_func_call_prov.assert_called_once()

        self.fc_prov._FunctionCallProv__outputs = {dumps(MyClass()):12}
        with patch(self.get_function_call_prov_entry_namespace, return_value=self.fc_prov) as get_func_call_prov:
            self.assertEqual(dumps(self.accurateMode.get_func_call_cache('func_call_hash')),
                             dumps(MyClass()))
            get_func_call_prov.assert_called_once()

    def test_func_call_acted_as_expected_when_metadata_returned_a_second_output(self):
        metadata = Metadata('func_call_hash', [], {}, True, 0)
        self.fc_prov._FunctionCallProv__outputs = {dumps(1):12}
        self.assertFalse(self.accurateMode.func_call_acted_as_expected(self.fc_prov, metadata))
        
    def test_func_call_acted_as_expected_when_function_outputs_already_had_more_than_one_output(self):
        metadata = Metadata('func_call_hash', [], {}, 1, 0)
        self.fc_prov._FunctionCallProv__outputs = {dumps(1):12,
                                                   dumps(False): 3}
        self.assertFalse(self.accurateMode.func_call_acted_as_expected(self.fc_prov, metadata))

    def test_func_call_acted_as_expected_when_function_acted_as_expected(self):
        metadata = Metadata('func_call_hash', [], {}, 1, 0)
        self.fc_prov._FunctionCallProv__outputs = {dumps(1):12}
        self.assertTrue(self.accurateMode.func_call_acted_as_expected(self.fc_prov, metadata))
        
    def test_func_call_acted_as_expected_when_function_acted_as_expected_with_different_data_types(self):
        metadata = Metadata('func_call_hash', [], {}, True, 0)
        self.fc_prov._FunctionCallProv__outputs = {dumps(True):12}
        self.assertTrue(self.accurateMode.func_call_acted_as_expected(self.fc_prov, metadata))

        metadata = Metadata('func_call_hash', [], {}, {1, 4, 'test', 7, MyClass()}, 0)
        self.fc_prov._FunctionCallProv__outputs = {dumps({1, 4, 'test', 7, MyClass()}):12}
        self.assertTrue(self.accurateMode.func_call_acted_as_expected(self.fc_prov, metadata))

        metadata = Metadata('func_call_hash', [], {}, MyClass(), 0)
        self.fc_prov._FunctionCallProv__outputs = {dumps(MyClass()):12}
        self.assertTrue(self.accurateMode.func_call_acted_as_expected(self.fc_prov, metadata))

        metadata = Metadata('func_call_hash', [], {}, (1, {2:False}, False, 7.123), 0)
        self.fc_prov._FunctionCallProv__outputs = {dumps((1, {2:False}, False, 7.123)):12}
        self.assertTrue(self.accurateMode.func_call_acted_as_expected(self.fc_prov, metadata))

class MyClass():
    def __init__(self):
        self.__x = 10
        self.__y = 20

if __name__ == '__main__':
    unittest.main()