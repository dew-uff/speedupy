import unittest, unittest.mock, os, sys, ast

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from services.experiment_service import _decorate_experiment_main_function
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
    
    def test_decorate_experiment_main_function(self):
        with open('script_test.py', 'wt') as f:
            f.write('import random, os, sys\nfrom matplotlib import pyplot as plt\n')
            f.write('from speedupy.intpy import initialize_intpy\n')
            f.write('@decorator1\n@decorator2(__file__)\ndef f1():\n\treturn "f1"\n')
            f.write('@f1\n@f2\n@initialize_intpy(__file__)\ndef main():\n\tf1(1, 2, 3)\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1], fileAST.body[2]]
        functions = {'f1':fileAST.body[3],
                     'main':fileAST.body[4]}
        script = Script('script_test.py', fileAST, imports, functions)
        experiment = Experiment('')
        experiment.add_script(script)
        experiment.set_main_script(script)

        _decorate_experiment_main_function(experiment)
        
        with open(script.name) as f1:
            code1 = f1.read().replace('@initialize_intpy(__file__)', '@execute_intpy')
            code2 = ast.unparse(script.AST)
            code1 = self.normalize_string(code1)
            code2 = self.normalize_string(code2)
            self.assertEqual(code1, code2)

if __name__ == '__main__':
    unittest.main()