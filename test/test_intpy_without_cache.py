import unittest, unittest.mock, os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import os

g_argsp_no_cache = True
g_argsp_m = None

class TestIntPyWithoutCache(unittest.TestCase):
    def setUp(self):
        os.system('rm -rf .intpy/')
        with open('constantes_test.py', 'wt') as arq:
            arq.write('g_argsp_m = None\ng_argsp_no_cache = True')

    def tearDown(self):
        os.system('rm -rf .intpy/')
        os.system('rm constantes_test.py')

    def test_deterministic_decorator(self):
        import intpy
        def my_function(a):
            return 2*a
        
        @intpy.deterministic
        def my_decorated_function(a):
            return 2*a
        
        self.assertEqual(my_function(10), my_decorated_function(10))
