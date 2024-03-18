import unittest, os, sys, inspect
import importlib

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.SpeeduPySettings import SpeeduPySettings
import speedupy

class TestSpeeduPy(unittest.TestCase):
    def test_initialize_speedupy_on_no_cache_exec_mode(self):
        SpeeduPySettings().exec_mode = ['no-cache']
        importlib.reload(speedupy)
        self.assertEqual(my_func, speedupy.initialize_speedupy(my_func))

    def test_deterministic_decorator_on_no_cache_exec_mode(self):
        SpeeduPySettings().exec_mode = ['no-cache']
        importlib.reload(speedupy)
        self.assertEqual(my_func, speedupy.deterministic(my_func))
        
    def test_maybe_deterministic_decorator_on_no_cache_exec_mode(self):
        SpeeduPySettings().exec_mode = ['no-cache']
        importlib.reload(speedupy)
        self.assertEqual(my_func, speedupy.maybe_deterministic(my_func))

    def test_maybe_deterministic_decorator_on_manual_exec_mode(self):
        SpeeduPySettings().exec_mode = ['manual']
        importlib.reload(speedupy)
        self.assertEqual(my_func, speedupy.maybe_deterministic(my_func))

    def test_initialize_speedupy_source_code_is_equal_on_manual_accurate_and_probabilistic_exec_modes(self):
        exec_modes = ['manual', 'accurate', 'probabilistic']
        func_source_codes = [] 
        for mode in exec_modes:
            SpeeduPySettings().exec_mode = [mode]
            importlib.reload(speedupy)
            func_source_codes.append(inspect.getsource(speedupy.initialize_speedupy))
        self.assertEqual(func_source_codes[0], func_source_codes[1])
        self.assertEqual(func_source_codes[1], func_source_codes[2])

    def test_deterministic_decorator_source_code_is_equal_on_manual_accurate_and_probabilistic_exec_modes(self):
        exec_modes = ['manual', 'accurate', 'probabilistic']
        func_source_codes = [] 
        for mode in exec_modes:
            SpeeduPySettings().exec_mode = [mode]
            importlib.reload(speedupy)
            func_source_codes.append(inspect.getsource(speedupy.deterministic))
        self.assertEqual(func_source_codes[0], func_source_codes[1])
        self.assertEqual(func_source_codes[1], func_source_codes[2])

    def test_maybe_deterministic_decorator_source_code_is_equal_on_accurate_and_probabilistic_exec_modes(self):
        exec_modes = ['accurate', 'probabilistic']
        func_source_codes = [] 
        for mode in exec_modes:
            SpeeduPySettings().exec_mode = [mode]
            importlib.reload(speedupy)
            func_source_codes.append(inspect.getsource(speedupy.maybe_deterministic))
        self.assertEqual(func_source_codes[0], func_source_codes[1])

def my_func(x, y):
    return x / y

if __name__ == '__main__':
    unittest.main()