import importlib
import inspect
import random
import unittest
from unittest.mock import Mock

import speedupy
from execute_exp.services.DataAccess import DataAccess
from execute_exp.SpeeduPySettings import SpeeduPySettings


class TestSpeeduPyExecMode(unittest.TestCase):
    def setUp(self):
        # The tests reload speedupy with other options and replace its attributes
        # by mocks: put the module and the settings back afterwards.
        for obj in (speedupy, SpeeduPySettings()):
            saved = dict(vars(obj))
            self.addCleanup(self._restore_attributes, obj, saved)
        SpeeduPySettings().measure_time = False
        SpeeduPySettings().profile = False

    @staticmethod
    def _restore_attributes(obj, saved):
        vars(obj).clear()
        vars(obj).update(saved)

    def test_initialize_speedupy_on_no_cache_exec_mode_without_time_measure(self):
        SpeeduPySettings().exec_mode = ["no-cache"]
        importlib.reload(speedupy)
        self.assertEqual(my_func, speedupy.initialize_speedupy(my_func))

    def test_initialize_speedupy_on_no_cache_exec_mode_with_time_measure(self):
        SpeeduPySettings().exec_mode = ["no-cache"]
        SpeeduPySettings().measure_time = True
        importlib.reload(speedupy)
        speedupy._measure_time = Mock()

        speedupy.initialize_speedupy(my_func)

        speedupy._measure_time.assert_called_once_with(my_func)

    def test_deterministic_decorator_on_no_cache_exec_mode(self):
        SpeeduPySettings().exec_mode = ["no-cache"]
        importlib.reload(speedupy)
        self.assertEqual(my_func, speedupy.deterministic(my_func))

    def test_maybe_deterministic_decorator_on_no_cache_exec_mode(self):
        SpeeduPySettings().exec_mode = ["no-cache"]
        importlib.reload(speedupy)
        self.assertEqual(my_func, speedupy.maybe_deterministic(my_func))

    def test_maybe_deterministic_decorator_on_manual_exec_mode(self):
        SpeeduPySettings().exec_mode = ["manual"]
        importlib.reload(speedupy)
        self.assertEqual(my_func, speedupy.maybe_deterministic(my_func))

    def test_initialize_speedupy_using_cache_exec_modes_with_and_without_time_measure_and_profile(
        self,
    ):
        exec_modes = [
            "manual",
            "accurate",
            "probabilistic-counting",
            "probabilistic-error",
        ]
        SpeeduPySettings().exec_mode = [random.choice(exec_modes)]
        SpeeduPySettings().measure_time = random.choice([True, False])
        SpeeduPySettings().profile = random.choice([True, False])

        importlib.reload(speedupy)
        speedupy.DataAccess = Mock(return_value=Mock(DataAccess))
        speedupy._measure_time = Mock(side_effect=lambda x: x)
        speedupy._profile = Mock(side_effect=lambda x: x)

        speedupy.initialize_speedupy(my_func)(2, 3)

        speedupy.DataAccess().init_data_access.assert_called_once_with()
        speedupy.DataAccess().close_data_access.assert_called_once_with()

        if SpeeduPySettings().measure_time:
            speedupy._measure_time.assert_called_once()
        else:
            speedupy._measure_time.assert_not_called()

        if SpeeduPySettings().profile:
            speedupy._profile.assert_called_once()
        else:
            speedupy._profile.assert_not_called()

    def test_initialize_speedupy_source_code_is_equal_on_manual_accurate_and_probabilistic_exec_modes(
        self,
    ):
        exec_modes = [
            "manual",
            "accurate",
            "probabilistic-counting",
            "probabilistic-error",
        ]
        func_source_codes = []
        for mode in exec_modes:
            SpeeduPySettings().exec_mode = [mode]
            importlib.reload(speedupy)
            func_source_codes.append(inspect.getsource(speedupy.initialize_speedupy))
        self.assertEqual(func_source_codes[0], func_source_codes[1])
        self.assertEqual(func_source_codes[1], func_source_codes[2])

    def test_deterministic_decorator_source_code_is_equal_on_manual_accurate_and_probabilistic_exec_modes(
        self,
    ):
        exec_modes = [
            "manual",
            "accurate",
            "probabilistic-counting",
            "probabilistic-error",
        ]
        func_source_codes = []
        for mode in exec_modes:
            SpeeduPySettings().exec_mode = [mode]
            importlib.reload(speedupy)
            func_source_codes.append(inspect.getsource(speedupy.deterministic))
        self.assertEqual(func_source_codes[0], func_source_codes[1])
        self.assertEqual(func_source_codes[1], func_source_codes[2])

    def test_maybe_deterministic_decorator_source_code_is_equal_on_accurate_and_probabilistic_exec_modes(
        self,
    ):
        exec_modes = ["accurate", "probabilistic-counting", "probabilistic-error"]
        func_source_codes = []
        for mode in exec_modes:
            SpeeduPySettings().exec_mode = [mode]
            importlib.reload(speedupy)
            func_source_codes.append(inspect.getsource(speedupy.maybe_deterministic))
        self.assertEqual(func_source_codes[0], func_source_codes[1])


def my_func(x, y):
    return x / y


if __name__ == "__main__":
    unittest.main()
