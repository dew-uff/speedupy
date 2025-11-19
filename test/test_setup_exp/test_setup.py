import unittest, os, sys, importlib
from unittest.mock import patch, MagicMock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

import setup_exp.setup as setup

class TestSetup(unittest.TestCase):
    def setUp(self):
        importlib.reload(setup)

    def tearDown(self):
        paths = ['.speedupy/', 'teste.xyz', 'teste.temp', 'folder1', 'folder2']
        for p in paths:
            os.system(f'rm -rf {p}')
    
    @patch('setup_exp.setup.init_env')
    @patch('setup_exp.setup.create_experiment')
    @patch('setup_exp.setup.analyze_experiment_function_call_hierarchy')
    @patch('setup_exp.setup.get_experiment_functions_hashes')
    @patch('setup_exp.setup.decorate_experiment_functions')
    @patch('setup_exp.setup.overwrite_decorated_experiment')
    @patch('setup_exp.setup.save_json_file')
    def test_setup_experiment_calls_init_env_with_correct_storage(self, 
                                                    mock_save, mock_overwrite, mock_decorate, 
                                                    mock_hashes, mock_analyze, mock_create, 
                                                    mock_init_env):
        
        storage_options = ['mysql', 'redis', 'mongo', 'sqlite', 'file']

        for storage_type in storage_options:
            args = MagicMock()
            args.main_script_path = 'script.py'
            args.storage = storage_type
            
            setup.setup_experiment(args)

            try:
                mock_init_env.assert_called_with(storage_type)
            except AssertionError as e:
                self.fail(f"Falha ao testar storage '{storage_type}': {e}")
            
            mock_init_env.reset_mock()

if __name__ == '__main__':
    unittest.main()