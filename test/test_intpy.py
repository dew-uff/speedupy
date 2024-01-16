import unittest, os, sys, ast
import importlib
from unittest.mock import patch, Mock
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from constantes import Constantes
import intpy

class TestIntPy(unittest.TestCase):
    def setUp(self):
        Constantes().g_argsp_no_cache = False
        importlib.reload(intpy)
        Constantes().FUNCTIONS_2_HASHES = {}
        Constantes().DONT_CACHE_FUNCTION_CALLS = []

    def test_deterministic_when_executing_speedupy_with_no_cache_arg(self):
        Constantes().g_argsp_no_cache = True
        importlib.reload(intpy)
        self.assertEqual(func, intpy.deterministic(func))
        
    def test_maybe_deterministic_when_executing_speedupy_with_no_cache_arg(self):
        Constantes().g_argsp_no_cache = True
        importlib.reload(intpy)
        self.assertEqual(func, intpy.maybe_deterministic(func))

    def test_maybe_deterministic_when_cache_hit(self):
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"func_hash"}
        Constantes().DONT_CACHE_FUNCTION_CALLS = ["hash1"]
        with patch('intpy.get_cache_data', return_value=2) as get_cache_data, \
             patch('intpy.get_id', return_value="func_call_hash") as get_id, \
             patch('intpy.add_to_metadata', return_value=None) as add_to_metadata:
            self.assertEqual(intpy.maybe_deterministic(func)(8, 4), 2)
            get_cache_data.assert_called_once()
            get_id.assert_not_called()
            add_to_metadata.assert_not_called()

    def test_maybe_deterministic_when_cache_miss_and_function_call_in_DONT_CACHE_FUNCTION_CALLS(self):
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"func_hash"}
        Constantes().DONT_CACHE_FUNCTION_CALLS = ["hash1", "func_call_hash"]
        with patch('intpy.get_cache_data', return_value=None) as get_cache_data, \
             patch('intpy.get_id', return_value="func_call_hash") as get_id, \
             patch('intpy.add_to_metadata', return_value=None) as add_to_metadata:
            self.assertEqual(intpy.maybe_deterministic(func)(8, 4), 2)
            get_cache_data.assert_called_once()
            get_id.assert_called_once()
            add_to_metadata.assert_not_called()

    def test_maybe_deterministic_when_cache_miss_and_function_call_not_in_DONT_CACHE_FUNCTION_CALLS(self):
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"func_hash"}
        Constantes().DONT_CACHE_FUNCTION_CALLS = ["hash1"]
        with patch('intpy.get_cache_data', return_value=None) as get_cache_data, \
             patch('intpy.get_id', return_value="func_call_hash") as get_id, \
             patch('intpy.add_to_metadata', return_value=None) as add_to_metadata:
            self.assertEqual(intpy.maybe_deterministic(func)(8, 4), 2)
            get_cache_data.assert_called_once()
            get_id.assert_called_once()
            add_to_metadata.assert_called_once()

    def test_collect_metadata_when_executing_speedupy_with_no_cache_arg(self):
        Constantes().g_argsp_no_cache = True
        importlib.reload(intpy)
        self.assertEqual(func, intpy.collect_metadata(func))

    def test_function_call_maybe_deterministic_when_DONT_CACHE_FUNCTION_CALLS_is_empty(self):
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"function_hash"}
        Constantes().DONT_CACHE_FUNCTION_CALLS = []
        with patch('intpy.get_id', return_value='function_call_hash'):
            self.assertTrue(intpy._function_call_maybe_deterministic(func, [1, 2], {}))
    
    def test_function_call_maybe_deterministic_when_function_call_in_DONT_CACHE_FUNCTION_CALLS(self):
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"function_hash"}
        Constantes().DONT_CACHE_FUNCTION_CALLS = ['function_call_hash']
        with patch('intpy.get_id', return_value='function_call_hash'):
            self.assertFalse(intpy._function_call_maybe_deterministic(func, [1, 2], {}))

    def test_function_call_maybe_deterministic_when_function_call_not_in_DONT_CACHE_FUNCTION_CALLS(self):
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"function_hash"}
        Constantes().DONT_CACHE_FUNCTION_CALLS = ['fc_hash_1', 'fc_hash_2', 'fc_hash_3']
        with patch('intpy.get_id', return_value='function_call_hash'):
            self.assertTrue(intpy._function_call_maybe_deterministic(func, [1, 2], {}))    

def func(x, y):
    return x / y

if __name__ == '__main__':
    unittest.main()