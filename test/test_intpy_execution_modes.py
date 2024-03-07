import unittest, os, sys, inspect
import importlib
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from constantes import Constantes
import speedupy

class TestIntPy(unittest.TestCase):
    def setUp(self):
        Constantes().g_argsp_exec_mode = 'manual'
        importlib.reload(speedupy)
        Constantes().FUNCTIONS_2_HASHES = {}
        Constantes().DONT_CACHE_FUNCTION_CALLS = []
    
    def test_execute_intpy_when_executing_speedupy_on_no_cache_exec_mode(self):
        Constantes().g_argsp_exec_mode = 'no-cache'
        importlib.reload(speedupy)
        self.assertEqual(func, speedupy.initialize_speedupy(func))

    def test_deterministic_when_executing_speedupy_on_no_cache_exec_mode(self):
        Constantes().g_argsp_exec_mode = 'no-cache'
        importlib.reload(speedupy)
        self.assertEqual(func, speedupy.deterministic(func))
        
    def test_maybe_deterministic_when_executing_speedupy_on_no_cache_exec_mode(self):
        Constantes().g_argsp_exec_mode = 'no-cache'
        importlib.reload(speedupy)
        self.assertEqual(func, speedupy.maybe_deterministic(func))

    def test_maybe_deterministic_when_executing_speedupy_on_manual_exec_mode(self):
        Constantes().g_argsp_exec_mode = 'manual'
        importlib.reload(speedupy)
        self.assertEqual(func, speedupy.maybe_deterministic(func))

    def test_execute_intpy_function_source_code_is_equal_on_manual_accurate_and_probabilistic_exec_modes(self):
        exec_modes = ['manual', 'accurate', 'probabilistic']
        func_source_codes = [] 
        for mode in exec_modes:
            Constantes().g_argsp_exec_mode = mode
            importlib.reload(speedupy)
            func_source_codes.append(inspect.getsource(speedupy.initialize_speedupy))
        self.assertEqual(func_source_codes[0], func_source_codes[1])
        self.assertEqual(func_source_codes[1], func_source_codes[2])

    def test_deterministic_function_source_code_is_equal_on_manual_accurate_and_probabilistic_exec_modes(self):
        exec_modes = ['manual', 'accurate', 'probabilistic']
        func_source_codes = [] 
        for mode in exec_modes:
            Constantes().g_argsp_exec_mode = mode
            importlib.reload(speedupy)
            func_source_codes.append(inspect.getsource(speedupy.deterministic))
        self.assertEqual(func_source_codes[0], func_source_codes[1])
        self.assertEqual(func_source_codes[1], func_source_codes[2])

    def test_maybe_deterministic_function_source_code_is_equal_on_accurate_and_probabilistic_exec_modes(self):
        exec_modes = ['accurate', 'probabilistic']
        func_source_codes = [] 
        for mode in exec_modes:
            Constantes().g_argsp_exec_mode = mode
            importlib.reload(speedupy)
            func_source_codes.append(inspect.getsource(speedupy.maybe_deterministic))
        self.assertEqual(func_source_codes[0], func_source_codes[1])

def func(x, y):
    return x / y

if __name__ == '__main__':
    unittest.main()