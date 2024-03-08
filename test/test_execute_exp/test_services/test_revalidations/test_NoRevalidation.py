import unittest, os, sys

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.revalidations.NoRevalidation import NoRevalidation

class TestNoRevalidation(unittest.TestCase):
    def setUp(self):
        self.noRevalidation = NoRevalidation()

    def test_revalidation_in_current_execution(self):
        for i in range(20):
            reval_exec = self.noRevalidation.revalidation_in_current_execution(f'func_call_hash_{i}')
            self.assertFalse(reval_exec)
    
if __name__ == '__main__':
    unittest.main()