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
    
    def test_validate_main_script_specified_when_no_script_was_specified(self):
        sys.argv = ['setup.py']
        self.assertRaises(Exception, setup.validate_main_script_specified)

    def test_validate_main_script_specified_when_main_script_was_specified(self):
        sys.argv = ['setup.py', 'main_script.py']
        setup.validate_main_script_specified()

    def test_validate_main_script_specified_when_many_scripts_were_specified(self):
        sys.argv = ['setup.py', 'script1.py', 'script2.py']
        self.assertRaises(Exception, setup.validate_main_script_specified)