import unittest, os, sys
from unittest.mock import patch

current = os.path.realpath(__file__).split('test/')[0]
print(f"current:{current}")
sys.path.append(current)

from services.execution_modes.ProbabilisticCountingMode import ProbabilisticCountingMode
from entities.FunctionCallProv import FunctionCallProv

class TestProbabilisticCountingMode(unittest.TestCase):
    def setUp(self):
        self.countingMode = ProbabilisticCountingMode()
        self.function_call_prov = FunctionCallProv(None, None, None, None, None, None, None, None, None, None, None, None, None)
        self.get_func_call_prov_namespace = 'services.execution_modes.ProbabilisticCountingMode.get_func_call_prov'
    
    def test_get_func_call_cache_with_different_output_types(self):
        self.function_call_prov.mode_output = 12
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.countingMode.get_func_call_cache('func_call_hash'), 12)
            get_func_call_prov.assert_called_once()
        
        self.function_call_prov.mode_output = 'my_result'
        with patch(self.get_func_call_prov_namespace, return_value=self.function_call_prov) as get_func_call_prov:
            self.assertEqual(self.countingMode.get_func_call_cache('func_call_hash'), 'my_result')
            get_func_call_prov.assert_called_once()

if __name__ == '__main__':
    unittest.main()