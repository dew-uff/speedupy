import unittest, os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from services.revalidations.NoRevalidation import NoRevalidation

class TestNoRevalidation(unittest.TestCase):
    def setUp(self):
        self.noRevalidation = NoRevalidation()

    def test_revalidation_in_current_execution(self):
        for i in range(20):
            reval_exec = self.noRevalidation.revalidation_in_current_execution(f'func_call_hash_{i}')
            self.assertFalse(reval_exec)
    
if __name__ == '__main__':
    unittest.main()