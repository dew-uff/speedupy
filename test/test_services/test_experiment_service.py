import unittest, unittest.mock, os, sys, ast

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from services.experiment_service import _prepare_experiment_main_script_for_execution, prepare_experiment_main_script_for_inference
from entities.Script import Script
from entities.Experiment import Experiment

class TestExperimentService(unittest.TestCase):
    def tearDown(self):
        files_and_folders = ['script_test.py', 
                             'script_test_2.py',
                             'script_test_3.py',
                             'folder',
                             'folder2',
                             'folder3',
                             'folder4',
                             '.intpy_temp']
        for f in files_and_folders:
            if os.path.exists(f):
                os.system(f'rm -rf {f}')
                #pass
    
    def getAST(self, nome_script:str) -> ast.Module:
        with open(nome_script, 'rt') as f:
            fileAST = ast.parse(f.read())
        return fileAST

    def normalize_string(self, string):
        return string.replace("\n\n", "\n").replace("\t", "    ").replace("\"", "'")
    
    def test_decorate_experiment_main_function_for_execution(self):
        with open('script_test.py', 'wt') as f:
            f.write(f"import sys\nsys.path.append('{os.getcwd()}')\n")
            f.write('from speedupy.intpy import deterministic, maybe_deterministic, collect_metadata\n')
            f.write('import random, os, sys\nfrom matplotlib import pyplot as plt\n')
            f.write('@decorator1\n@decorator2(__file__)\ndef f1():\n\treturn "f1"\n')
            f.write('@f1\n@f2\n@initialize_intpy(__file__)\ndef main():\n\tf1(1, 2, 3)\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[2], fileAST.body[3], fileAST.body[4]]
        functions = {'f1':fileAST.body[5],
                     'main':fileAST.body[6]}
        script = Script('script_test.py', fileAST, imports, functions)
        experiment = Experiment('')
        experiment.add_script(script)
        experiment.set_main_script(script)

        _prepare_experiment_main_script_for_execution(experiment)
        
        with open(script.name) as f1:
            code1 = f1.read().replace('@initialize_intpy(__file__)', '@execute_intpy')\
                             .replace('collect_metadata\n', 'collect_metadata\nfrom speedupy.intpy import execute_intpy\n')
            code2 = ast.unparse(script.AST)
            code1 = self.normalize_string(code1)
            code2 = self.normalize_string(code2)
            self.assertEqual(code1, code2)
    
    def test_prepare_experiment_main_script_for_inference(self):
        with open('script_test.py', 'wt') as f:
            f.write(f"import sys\nsys.path.append('{os.getcwd()}')\n")
            f.write('from speedupy.intpy import deterministic, maybe_deterministic, collect_metadata\n')
            f.write('from speedupy.intpy import execute_intpy\n')
            f.write('import random, os, sys\nfrom matplotlib import pyplot as plt\n')
            f.write('@decorator1\n@decorator2(__file__)\ndef f1():\n\treturn "f1"\n')
            f.write('@f1\n@f2\n@execute_intpy\ndef main():\n\tf1(1, 2, 3)\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[2], fileAST.body[3], fileAST.body[4], fileAST.body[5]]
        functions = {'f1':fileAST.body[6],
                     'main':fileAST.body[7]}
        script = Script('script_test.py', fileAST, imports, functions)
        experiment = Experiment('')
        experiment.add_script(script)
        experiment.set_main_script(script)

        prepare_experiment_main_script_for_inference(experiment)
        
        with open(script.name) as f1:
            code1 = f1.read().replace('@execute_intpy', '@start_inference_engine')\
                             .replace('from speedupy.intpy import execute_intpy', 'from speedupy.function_inference_engine import start_inference_engine')
            code2 = ast.unparse(script.AST)
            code1 = self.normalize_string(code1)
            code2 = self.normalize_string(code2)
            self.assertEqual(code1, code2)

if __name__ == '__main__':
    unittest.main()