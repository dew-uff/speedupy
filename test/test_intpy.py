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
    
    def test_deterministic_when_cache_hit(self):
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"func_hash"}
        with patch('intpy.get_cache_data', return_value=2) as get_cache_data, \
             patch('intpy.add_to_cache', return_value=None) as add_to_cache:
            self.assertEqual(intpy.deterministic(func)(8, 4), 2)
            get_cache_data.assert_called_once()
            add_to_cache.assert_not_called()

    def test_deterministic_when_cache_miss(self):
        Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"func_hash"}
        with patch('intpy.get_cache_data', return_value=None) as get_cache_data, \
             patch('intpy.add_to_cache', return_value=None) as add_to_cache:
            self.assertEqual(intpy.deterministic(func)(8, 4), 2)
            get_cache_data.assert_called_once()
            add_to_cache.assert_called_once()
        
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

    def test_simulate_func_exec_func_with_four_possible_returns_returning_first_value(self):
        with patch('random.random', return_value=0.1):
            returns_2_freq = {1:0.2, 3:0.4, 5:0.1, 7:0.3}
            self.assertEqual(intpy._simulate_func_exec(returns_2_freq), 1)

    def test_simulate_func_exec_func_with_four_possible_returns_returning_third_value(self):
        with patch('random.random', return_value=0.61):
            returns_2_freq = {1:0.2, 3:0.4, 5:0.1, 7:0.3}
            self.assertEqual(intpy._simulate_func_exec(returns_2_freq), 5)

    def test_simulate_func_exec_func_with_four_possible_returns_returning_fourth_value(self):
        with patch('random.random', return_value=0.8):
            returns_2_freq = {1:0.2, 3:0.4, 5:0.1, 7:0.3}
            self.assertEqual(intpy._simulate_func_exec(returns_2_freq), 7)

    def test_simulate_func_exec_func_when_sorted_number_is_in_the_limit_to_select_a_value(self):
        with patch('random.random', return_value=0.6):
            returns_2_freq = {1:0.2, 3:0.4, 5:0.1, 7:0.3}
            self.assertEqual(intpy._simulate_func_exec(returns_2_freq), 3)

def func(x, y):
    return x / y

if __name__ == '__main__':
    unittest.main()