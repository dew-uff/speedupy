import unittest, os, sys
from pickle import dumps, loads
from unittest.mock import patch

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from services.execution_modes.AccurateMode import AccurateMode
from entities.FunctionCallProv import FunctionCallProv

class TestAccurateMode(unittest.TestCase):
    def setUp(self):
        self.accurateMode = AccurateMode()
        self.function_call_prov = FunctionCallProv(None, None, None, None, None, None, None, None, None, None, None, None, None)
        self.get_func_call_prov_namespace = 'services.execution_modes.AccurateMode.get_func_call_prov'
    
    def test_func_call_can_be_cached_when_func_has_one_output(self):
        self.function_call_prov._FunctionCallProv__outputs = {dumps(1):12}
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertTrue(self.accurateMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
    
    def test_func_call_can_be_cached_when_func_has_2_outputs(self):
        self.function_call_prov._FunctionCallProv__outputs = {dumps(2): 5,
                                                              dumps(3): 3}
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertFalse(self.accurateMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()

    def test_func_call_can_be_cached_when_func_has_many_outputs(self):
        self.function_call_prov._FunctionCallProv__outputs = {dumps(1):12,
                                                              dumps(2):5,
                                                              dumps(3):3,
                                                              dumps(4):1}
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertFalse(self.accurateMode.func_call_can_be_cached('func_call_hash'))
            get_func_call_prov.assert_called_once()
    
    def test_get_func_call_cache_with_different_types(self):
        self.function_call_prov._FunctionCallProv__outputs = {dumps(1):12}
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.accurateMode.get_func_call_cache('func_call_hash'), 1)
            get_func_call_prov.assert_called_once()

        self.function_call_prov._FunctionCallProv__outputs = {dumps('my_result'):12}
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.accurateMode.get_func_call_cache('func_call_hash'), 'my_result')
            get_func_call_prov.assert_called_once()

        self.function_call_prov._FunctionCallProv__outputs = {dumps({1, 2, 3}):12}
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.accurateMode.get_func_call_cache('func_call_hash'), {1, 2, 3})
            get_func_call_prov.assert_called_once()

        self.function_call_prov._FunctionCallProv__outputs = {dumps(MyClass()):12}
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(dumps(self.accurateMode.get_func_call_cache('func_call_hash')),
                             dumps(MyClass()))
            get_func_call_prov.assert_called_once()

class MyClass():
    def __init__(self):
        self.__x = 10
        self.__y = 20

if __name__ == '__main__':
    unittest.main()