import unittest, unittest.mock, os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from constantes import Constantes

g_argsp_no_cache = True
g_argsp_m = None

class TestInitializeIntPy(unittest.TestCase):
    def setUp(self):
        os.system('rm -rf .intpy/')

    def tearDown(self):
        os.system('rm -rf .intpy/')

    def test_deterministic_decorator(self):
        Constantes().g_argsp_m = None
        Constantes().g_argsp_no_cache = True

        from initialize_intpy import initialize_intpy
        
        self.aux = 0
        def my_function(value):
            self.aux = value
                
        my_function(10)
        self.assertEqual(self.aux, 10)

        initialize_intpy(__file__)(my_function)(-3)
        self.assertEqual(self.aux, -3)
