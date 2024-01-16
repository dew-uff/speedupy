import unittest, os, sys, ast
from unittest.mock import patch, Mock

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from constantes import Constantes
from intpy import _function_call_maybe_deterministic
class TestIntPy(unittest.TestCase):
    def test_function_call_maybe_deterministic_when_DONT_CACHE_FUNCTION_CALLS_is_empty(self):
        def func(x, y):
            return x / y
        Constantes().g_argsp_no_cache = False
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"function_hash"}
        Constantes().DONT_CACHE_FUNCTION_CALLS = []
        with patch('intpy.get_id', return_value='function_call_hash'):
            self.assertTrue(_function_call_maybe_deterministic(func, [1, 2], {}))
    
    def test_function_call_maybe_deterministic_when_function_call_in_DONT_CACHE_FUNCTION_CALLS(self):
        def func(x, y):
            return x / y
        Constantes().g_argsp_no_cache = False
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"function_hash"}
        Constantes().DONT_CACHE_FUNCTION_CALLS = ['function_call_hash']
        with patch('intpy.get_id', return_value='function_call_hash'):
            self.assertFalse(_function_call_maybe_deterministic(func, [1, 2], {}))

    def test_function_call_maybe_deterministic_when_function_call_not_in_DONT_CACHE_FUNCTION_CALLS(self):
        def func(x, y):
            return x / y
        Constantes().g_argsp_no_cache = False
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"function_hash"}
        Constantes().DONT_CACHE_FUNCTION_CALLS = ['fc_hash_1', 'fc_hash_2', 'fc_hash_3']
        with patch('intpy.get_id', return_value='function_call_hash'):
            self.assertTrue(_function_call_maybe_deterministic(func, [1, 2], {}))    

if __name__ == '__main__':
    unittest.main()