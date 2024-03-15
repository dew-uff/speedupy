import unittest, os, sys, io
from unittest.mock import patch

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.SpeeduPySettings import SpeeduPySettings

class TestIntPy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = SpeeduPySettings()

    def test_validate_user_args_with_correct_args(self):
        self.settings.exec_mode = 'accurate'
        
        self.settings._validate_user_args()
        self.assertEqual(self.settings.exec_mode, 'accurate')
        
    def test_validate_user_args_without_exec_mode_nor_strategy(self):
        self.settings.exec_mode = None
        self.settings.strategy = None
        
        self.settings._validate_user_args()
        self.assertEqual(self.settings.exec_mode, 'manual')
        self.assertIsNone(self.settings.strategy)

    def test_validate_user_args_without_exec_mode_but_with_strategy(self):
        self.settings.exec_mode = None
        self.settings.strategy = 'counting'
        
        self.settings._validate_user_args()
        self.assertEqual(self.settings.exec_mode, 'probabilistic')
        self.assertEqual(self.settings.strategy, 'counting')

    def test_validate_user_args_with_probabilistic_mode_without_strategy(self):
        self.settings.exec_mode = 'probabilistic'
        self.settings.strategy = None
        
        self.settings._validate_user_args()
        self.assertEqual(self.settings.exec_mode, 'probabilistic')
        self.assertEqual(self.settings.strategy, 'error')
