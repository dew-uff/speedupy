import unittest, os, sys, random
from unittest.mock import patch, Mock
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from execute_exp.services.Profiler import Profiler
from speedupy import deterministic, _execute_func_measuring_time

class TestSpeeduPy(unittest.TestCase):
    def setUp(self):
        self.fc_hash = 'fc_hash'

        self.patcher_DataAccess = patch('speedupy.DataAccess')
        self.dataAccess = self.patcher_DataAccess.start().return_value
        self.dataAccess.get_id = Mock(return_value=self.fc_hash)
        self.dataAccess.get_cache_entry = Mock(return_value=None)
        self.dataAccess.create_cache_entry = Mock(return_value=None)

        self.patcher_Speedupy = patch('speedupy.SpeeduPy')
        self.speedupy = self.patcher_Speedupy.start().return_value
        self.speedupy.min_exec_time_to_memoize = 0

        Profiler().num_deterministic_calls = 0
        Profiler().num_cache_hit = 0
        Profiler().num_func_call_too_fast_to_memoize = 0

    def tearDown(self):
        self.patcher_DataAccess.stop()
        self.patcher_Speedupy.stop()

    @patch('sys.stderr')
    @patch('sys.stdout')
    def test_deterministic_when_cache_hit(self, mock_stdout, mock_stderr):
        from test_helpers import func

        self.dataAccess.get_cache_entry = Mock(return_value=(2, "stdout msg\n", "stderr msg\n"))

        self.assertEqual(Profiler().num_deterministic_calls, 0)
        self.assertEqual(Profiler().num_cache_hit, 0)
        self.assertEqual(Profiler().num_func_call_too_fast_to_memoize, 0)
        self.assertEqual(func(8, v=4, func_globals=globals()), 2)
        self.assertEqual(Profiler().num_deterministic_calls, 1)
        self.assertEqual(Profiler().num_cache_hit, 1)
        self.assertEqual(Profiler().num_func_call_too_fast_to_memoize, 0)

        self.dataAccess.get_id.assert_called_once_with(func.__qualname__, (8,), {'v': 4})
        self.dataAccess.get_cache_entry.assert_called_once_with(self.fc_hash, func.__qualname__)
        mock_stdout.write.assert_called_with("stdout msg\n")
        mock_stderr.write.assert_called_with("stderr msg\n")
        self.dataAccess.create_cache_entry.assert_not_called()

    @patch('sys.stderr')
    @patch('sys.stdout')
    def test_deterministic_when_cache_miss(self, mock_stdout, mock_stderr):
        from test_helpers import func

        self.assertEqual(Profiler().num_deterministic_calls, 0)
        self.assertEqual(Profiler().num_cache_hit, 0)
        self.assertEqual(Profiler().num_func_call_too_fast_to_memoize, 0)
        self.assertEqual(func(8, v=1, func_globals=globals()), 2)
        self.assertEqual(Profiler().num_deterministic_calls, 1)
        self.assertEqual(Profiler().num_cache_hit, 0)
        self.assertEqual(Profiler().num_func_call_too_fast_to_memoize, 0)

        self.dataAccess.get_id.assert_called_once_with(func.__qualname__, (8,), {'v': 1})
        self.dataAccess.get_cache_entry.assert_called_once_with(self.fc_hash, func.__qualname__)
        mock_stdout.write.assert_called_with("stdout msg\n")
        mock_stderr.write.assert_called_with("stderr msg\n")
        self.dataAccess.create_cache_entry.assert_called_once_with(self.fc_hash, (2, "stdout msg\n", "stderr msg\n"), func.__qualname__)

    def test_deterministic_when_function_has_no_args(self):
        @deterministic
        def func(x=10, y=20, z=30, func_globals={}):
            return False

        self.assertFalse(func(x=1, y=2, z=3, func_globals=globals()))

        self.dataAccess.get_id.assert_called_once_with(func.__qualname__, (), {'x': 1, 'y': 2, 'z': 3})
        self.dataAccess.get_cache_entry.assert_called_once_with(self.fc_hash, func.__qualname__)
        self.dataAccess.create_cache_entry.assert_called_once_with(self.fc_hash, (False, '', ''), func.__qualname__)

    def test_deterministic_when_function_has_no_kwargs(self):
        @deterministic
        def func(i, j, k, func_globals={}):
            return {'my', 'set', '!'}

        self.assertSetEqual(func(1, 2, 3, func_globals=globals()), {'my', 'set', '!'})

        self.dataAccess.get_id.assert_called_once_with(func.__qualname__, (1, 2, 3), {})
        self.dataAccess.get_cache_entry.assert_called_once_with(self.fc_hash, func.__qualname__)
        self.dataAccess.create_cache_entry.assert_called_once_with(self.fc_hash, ({'my', 'set', '!'}, '', ''), func.__qualname__)

    def test_deterministic_when_function_has_no_input(self):
        @deterministic
        def func(func_globals={}):
            return ['my', -2.3, False]

        self.assertListEqual(func(func_globals=globals()), ['my', -2.3, False])

        self.dataAccess.get_id.assert_called_once_with(func.__qualname__, (), {})
        self.dataAccess.get_cache_entry.assert_called_once_with(self.fc_hash, func.__qualname__)
        self.dataAccess.create_cache_entry.assert_called_once_with(self.fc_hash, (['my', -2.3, False], '', ''), func.__qualname__)

    def test_deterministic_when_cache_miss_occurs_but_function_args_and_kwargs_are_changed_during_the_execution_of_the_pure_function(self):
        @deterministic
        def func(lista: list, s: set = {}, func_globals={}):
            lista.pop()
            s.remove('a')
            return lista, s

        def get_id_side_effect(*args):
            if args == (func.__qualname__, ([1, 2, 3],), {'s': {'a', 'b', 'c'}}): return 'fc_hash'

            raise Exception()

        self.dataAccess.get_id.side_effect=get_id_side_effect

        def create_cache_entry_side_effect(*args):
            if args == ('fc_hash', (([1, 2], {'b', 'c'}), '', ''), func.__qualname__): return

            raise Exception()

        self.dataAccess.create_cache_entry.side_effect=create_cache_entry_side_effect

        lista = [1, 2, 3]
        conjunto = {'a', 'b', 'c'}

        func(lista, s=conjunto, func_globals=globals())

        self.assertListEqual(lista, [1, 2])
        self.assertSetEqual(conjunto, {'b', 'c'})
        self.dataAccess.get_id.assert_called_once()
        self.dataAccess.get_cache_entry.assert_called_once_with(self.fc_hash, func.__qualname__)
        self.dataAccess.create_cache_entry.assert_called_once()

    @patch('sys.stderr')
    @patch('sys.stdout')
    def test_deterministic_when_function_call_executes_below_min_exec_time_to_memoize(self, mock_stdout, mock_stderr):
        from test_helpers import func
        globals()['func'] = func

        self.speedupy.min_exec_time_to_memoize = 1
        wrapped = func.__wrapped__

        self.assertEqual(Profiler().num_deterministic_calls, 0)
        self.assertEqual(Profiler().num_cache_hit, 0)
        self.assertEqual(Profiler().num_func_call_too_fast_to_memoize, 0)
        self.assertEqual(globals()[func.__name__], func)
        self.assertEqual(func(8, v=1, func_globals=globals()), 2)
        self.assertEqual(Profiler().num_deterministic_calls, 1)
        self.assertEqual(Profiler().num_cache_hit, 0)
        self.assertEqual(Profiler().num_func_call_too_fast_to_memoize, 1)
        self.assertEqual(globals()[func.__name__], wrapped)

        self.dataAccess.get_id.assert_called_once_with(func.__qualname__, (8,), {'v': 1})
        self.dataAccess.get_cache_entry.assert_called_once_with(self.fc_hash, func.__qualname__)
        mock_stdout.write.assert_called_with("stdout msg\n")
        mock_stderr.write.assert_called_with("stderr msg\n")
        self.dataAccess.create_cache_entry.assert_not_called()

        globals().pop('func')

    @patch('sys.stderr')
    @patch('sys.stdout')
    def test_deterministic_when_function_call_executes_above_min_exec_time_to_memoize(self, mock_stdout, mock_stderr):
        from test_helpers import func
        globals()['func'] = func

        self.assertEqual(Profiler().num_deterministic_calls, 0)
        self.assertEqual(Profiler().num_cache_hit, 0)
        self.assertEqual(Profiler().num_func_call_too_fast_to_memoize, 0)
        self.assertEqual(globals()[func.__name__], func)
        self.assertEqual(func(8, v=1, func_globals=globals()), 2)
        self.assertEqual(Profiler().num_deterministic_calls, 1)
        self.assertEqual(Profiler().num_cache_hit, 0)
        self.assertEqual(Profiler().num_func_call_too_fast_to_memoize, 0)
        self.assertEqual(globals()[func.__name__], func)

        self.dataAccess.get_id.assert_called_once_with(func.__qualname__, (8,), {'v': 1})
        self.dataAccess.get_cache_entry.assert_called_once_with(self.fc_hash, func.__qualname__)
        mock_stdout.write.assert_called_with("stdout msg\n")
        mock_stderr.write.assert_called_with("stderr msg\n")
        self.dataAccess.create_cache_entry.assert_called_once_with(self.fc_hash, (2, "stdout msg\n", "stderr msg\n"), func.__qualname__)

        globals().pop('func')

    def test_execute_func_measuring_time_when_a_function_is_passed(self):
        def func2(a, b, c, x=1, y=True):
            return 20

        result, _ = _execute_func_measuring_time(func2, (1, 3, 2), {'x': 1.213, 'y': False})
        self.assertEqual(result, 20)

    def test_execute_func_measuring_time_when_an_instance_method_is_passed(self):
        class MyClass():
            def my_method(self, a, b, c, x=1, y=True):
                return True

        result, _ = _execute_func_measuring_time(MyClass().my_method, (1, 3, 2), {'x': 1.213, 'y': False})
        self.assertTrue(result)

    def test_execute_func_measuring_time_when_a_class_method_is_passed(self):
        class MyClass():
            @classmethod
            def my_classmethod(cls, a, b, c, x=1, y=True):
                return {-b, c * c, x + a, y}

        result, _ = _execute_func_measuring_time(MyClass.my_classmethod, (1, 3, 2), {'x': 1.213, 'y': False})
        self.assertSetEqual(result, {-3, 4, 2.213, False})

    def test_execute_func_measuring_time_when_a_function_without_args_is_passed(self):
        def func2(x=1.12312, y=[1, 5, 2]):
            return 3.14

        result, _ = _execute_func_measuring_time(func2, (), {'x': 1.213, 'y': [3]})
        self.assertEqual(result, 3.14)

    def test_execute_func_measuring_time_when_a_function_without_kwargs_is_passed(self):
        def func2(a, b, c):
            return False

        result, _ = _execute_func_measuring_time(func2, (1, 3, 2), {})
        self.assertFalse(result)

    def test_execute_func_measuring_time_when_a_function_without_input_is_passed(self):
        def func2():
            return 1000

        result, _ = _execute_func_measuring_time(func2, (), {})
        self.assertEqual(result, 1000)


if __name__ == '__main__':
    unittest.main()
