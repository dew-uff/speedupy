import unittest, os, sys, importlib
from unittest.mock import patch

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import setup

class TestSetup(unittest.TestCase):
    def setUp(self):
        importlib.reload(sys)

    def tearDown(self):
        paths = ['.intpy/', '.intpy_temp/', 'teste.xyz', 'teste.temp', 'folder1', 'folder2']
        for p in paths:
            os.system(f'rm -rf {p}')

    def test_check_python_version_with_minimum_version(self):
        sys.version_info=(3, 9)
        setup.check_python_version()

    def test_check_python_version_with_correct_version_greater_than_minimum(self):
        sys.version_info=(3, 12)
        setup.check_python_version()

    def test_check_python_version_with_incorrect_version_greater_than_minimum(self):
        sys.version_info=(4, 1)
        self.assertRaises(Exception, setup.check_python_version)

    def test_check_python_version_with_incorrect_version_lower_than_minimum(self):
        sys.version_info=(2, 7)
        self.assertRaises(Exception, setup.check_python_version)
    
    def test_validate_main_script_specified_when_no_script_was_specified(self):
        sys.argv = ['setup.py']
        self.assertRaises(Exception, setup.validate_main_script_specified)

    def test_validate_main_script_specified_when_main_script_was_specified(self):
        sys.argv = ['setup.py', 'main_script.py']
        setup.validate_main_script_specified()

    def test_validate_main_script_specified_when_many_scripts_were_specified(self):
        sys.argv = ['setup.py', 'script1.py', 'script2.py']
        self.assertRaises(Exception, setup.validate_main_script_specified)