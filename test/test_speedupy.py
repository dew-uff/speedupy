import unittest, os, sys
from unittest.mock import patch, Mock
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from execute_exp.services.DataAccess import DataAccess
from speedupy import deterministic, _execute_func_measuring_time

class TestSpeeduPy(unittest.TestCase):
    def setUp(self):
        self.dataAccess = Mock(DataAccess)

    def test_deterministic_when_cache_hit(self):
        with patch('speedupy.DataAccess', return_value=self.dataAccess):
            self.dataAccess.get_cache_entry = Mock(return_value=10)
            self.dataAccess.create_cache_entry = Mock()
            func = Mock()
            func.__qualname__ = 'func'

            self.assertEqual(deterministic(func)(8, 4), 10)

            self.dataAccess.get_cache_entry.assert_called_once()
            self.assertTupleEqual(self.dataAccess.get_cache_entry.call_args.args,
                                  ('func', (8, 4), {}))
            func.assert_not_called()
            self.dataAccess.create_cache_entry.assert_not_called()

    def test_deterministic_when_cache_miss(self):
        with patch('speedupy.DataAccess', return_value=self.dataAccess):
            self.dataAccess.get_cache_entry = Mock(return_value=None)
            self.dataAccess.create_cache_entry = Mock()
            func = Mock(return_value=2)
            func.__qualname__ = 'func'

            self.assertEqual(deterministic(func)(8, v=1), 2)


            self.dataAccess.get_cache_entry.assert_called_once()
            self.assertTupleEqual(self.dataAccess.get_cache_entry.call_args.args,
                                  ('func', (8,), {'v':1}))
            
            func.assert_called_once()
            self.assertTupleEqual(func.call_args.args, (8,))
            self.assertDictEqual(func.call_args.kwargs, {'v':1})
            
            self.dataAccess.create_cache_entry.assert_called_once()
            self.assertTupleEqual(self.dataAccess.create_cache_entry.call_args.args,
                                  ('func', (8,), {'v':1}, 2))

    def test_deterministic_when_function_has_no_args(self):
        with patch('speedupy.DataAccess', return_value=self.dataAccess):
            self.dataAccess.get_cache_entry = Mock(return_value=None)
            self.dataAccess.create_cache_entry = Mock()
            func = Mock(return_value=False)
            func.__qualname__ = 'func'

            self.assertFalse(deterministic(func)(x=1, y=2, z=3))


            self.dataAccess.get_cache_entry.assert_called_once()
            self.assertTupleEqual(self.dataAccess.get_cache_entry.call_args.args,
                                  ('func', (), {'x':1, 'y':2, 'z':3}))
            
            func.assert_called_once()
            self.assertTupleEqual(func.call_args.args, ())
            self.assertDictEqual(func.call_args.kwargs, {'x':1, 'y':2, 'z':3})
            
            self.dataAccess.create_cache_entry.assert_called_once()
            self.assertTupleEqual(self.dataAccess.create_cache_entry.call_args.args,
                                  ('func', (), {'x':1, 'y':2, 'z':3}, False))

    def test_deterministic_when_function_has_no_kwargs(self):
        with patch('speedupy.DataAccess', return_value=self.dataAccess):
            self.dataAccess.get_cache_entry = Mock(return_value=None)
            self.dataAccess.create_cache_entry = Mock()
            func = Mock(return_value={'my', 'set', '!'})
            func.__qualname__ = 'func'

            self.assertSetEqual(deterministic(func)(1, 2, 3), {'my', 'set', '!'})


            self.dataAccess.get_cache_entry.assert_called_once()
            self.assertTupleEqual(self.dataAccess.get_cache_entry.call_args.args,
                                  ('func', (1, 2, 3), {}))
            
            func.assert_called_once()
            self.assertTupleEqual(func.call_args.args, (1, 2, 3))
            self.assertDictEqual(func.call_args.kwargs, {})
            
            self.dataAccess.create_cache_entry.assert_called_once()
            self.assertTupleEqual(self.dataAccess.create_cache_entry.call_args.args,
                                  ('func', (1, 2, 3), {}, {'my', 'set', '!'}))

    def test_deterministic_when_function_has_no_input(self):
        with patch('speedupy.DataAccess', return_value=self.dataAccess):
            self.dataAccess.get_cache_entry = Mock(return_value=None)
            self.dataAccess.create_cache_entry = Mock()
            func = Mock(return_value=['my', -2.3, False])
            func.__qualname__ = 'func'

            self.assertListEqual(deterministic(func)(), ['my', -2.3, False])


            self.dataAccess.get_cache_entry.assert_called_once()
            self.assertTupleEqual(self.dataAccess.get_cache_entry.call_args.args,
                                  ('func', (), {}))
            
            func.assert_called_once()
            self.assertTupleEqual(func.call_args.args, ())
            self.assertDictEqual(func.call_args.kwargs, {})
            
            self.dataAccess.create_cache_entry.assert_called_once()
            self.assertTupleEqual(self.dataAccess.create_cache_entry.call_args.args,
                                  ('func', (), {}, ['my', -2.3, False])) 

    def test_execute_func_measuring_time_when_a_function_is_passed(self):
        def func2(a, b, c, x=1, y=True):
            return 20

        result, _ = _execute_func_measuring_time(func2, (1, 3, 2), {'x':1.213, 'y':False})
        self.assertEqual(result, 20)
            
    def test_execute_func_measuring_time_when_an_instance_method_is_passed(self):
        class MyClass():
            def my_method(self, a, b, c, x=1, y=True):
                return True

        result, _ = _execute_func_measuring_time(MyClass().my_method, (1, 3, 2), {'x':1.213, 'y':False})
        self.assertTrue(result)

    def test_execute_func_measuring_time_when_a_class_method_is_passed(self):
        class MyClass():
            @classmethod
            def my_classmethod(cls, a, b, c, x=1, y=True):
                return {-b, c*c, x+a, y}

        result, _ = _execute_func_measuring_time(MyClass.my_classmethod, (1, 3, 2), {'x':1.213, 'y':False})
        self.assertSetEqual(result, {-3, 4, 2.213, False})

    def test_execute_func_measuring_time_when_a_function_without_args_is_passed(self):
        def func2(x=1.12312, y=[1, 5, 2]):
            return 3.14

        result, _ = _execute_func_measuring_time(func2, (), {'x':1.213, 'y':[3]})
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

    # TODO: When testing @maybe_deterministic maybe some of these tests may be used!
    # def test_maybe_deterministic_when_cache_hit(self):
    #     Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"func_hash"}
    #     Constantes().DONT_CACHE_FUNCTION_CALLS = ["hash1"]
    #     with patch('intpy.get_cache_data', return_value=2) as get_cache_data, \
    #          patch('intpy.get_function_call_return_freqs', return_value=None) as get_func_call_return_freqs, \
    #          patch('random.random') as random, \
    #          patch('intpy.get_id') as get_id, \
    #          patch('intpy.add_to_metadata') as add_to_metadata:
    #         self.assertEqual(speedupy.maybe_deterministic(func)(8, 4), 2)
    #         get_cache_data.assert_called_once()
    #         get_func_call_return_freqs.assert_called_once()
    #         random.assert_not_called()
    #         get_id.assert_not_called()
    #         add_to_metadata.assert_not_called()

    # def test_maybe_deterministic_when_function_call_is_simulated(self):
    #     Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"func_hash"}
    #     Constantes().DONT_CACHE_FUNCTION_CALLS = ["hash1"]
    #     with patch('intpy.get_cache_data', return_value=None) as get_cache_data, \
    #          patch('intpy.get_function_call_return_freqs', return_value={0:0.5, 1:0.5}) as get_func_call_return_freqs, \
    #          patch('random.random', return_value=0.6) as random, \
    #          patch('intpy.get_id') as get_id, \
    #          patch('intpy.add_to_metadata') as add_to_metadata:
    #         self.assertEqual(speedupy.maybe_deterministic(func)(8, 4), 1)
    #         get_cache_data.assert_called_once()
    #         get_func_call_return_freqs.assert_called_once()
    #         random.assert_called_once()
    #         get_id.assert_not_called()
    #         add_to_metadata.assert_not_called()

    # def test_maybe_deterministic_when_function_call_in_DONT_CACHE_FUNCTION_CALLS(self):
    #     Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"func_hash"}
    #     Constantes().DONT_CACHE_FUNCTION_CALLS = ["hash1", "func_call_hash"]
    #     with patch('intpy.get_cache_data', return_value=None) as get_cache_data, \
    #          patch('intpy.get_function_call_return_freqs', return_value=None) as get_func_call_return_freqs, \
    #          patch('random.random') as random, \
    #          patch('intpy.get_id', return_value='func_call_hash') as get_id, \
    #          patch('intpy.add_to_metadata') as add_to_metadata:
    #         self.assertEqual(speedupy.maybe_deterministic(func)(8, 4), 2)
    #         get_cache_data.assert_called_once()
    #         get_func_call_return_freqs.assert_called_once()
    #         random.assert_not_called()
    #         get_id.assert_called_once()
    #         add_to_metadata.assert_not_called()

    # def test_maybe_deterministic_when_function_need_to_execute_and_can_collect_metadata(self):
    #     Constantes().FUNCTIONS_2_HASHES = {func.__qualname__:"func_hash"}
    #     Constantes().DONT_CACHE_FUNCTION_CALLS = ["hash1"]
    #     with patch('intpy.get_cache_data', return_value=None) as get_cache_data, \
    #          patch('intpy.get_function_call_return_freqs', return_value=None) as get_func_call_return_freqs, \
    #          patch('random.random') as random, \
    #          patch('intpy.get_id', return_value='func_call_hash') as get_id, \
    #          patch('intpy.add_to_metadata', return_value=None) as add_to_metadata:
    #         self.assertEqual(speedupy.maybe_deterministic(func)(8, 4), 2)
    #         get_cache_data.assert_called_once()
    #         get_func_call_return_freqs.assert_called_once()
    #         random.assert_not_called()
    #         get_id.assert_called_once()
    #         add_to_metadata.assert_called_once()
 
def func(x, y):
    return x / y

if __name__ == '__main__':
    unittest.main()