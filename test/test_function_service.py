from typing import List, Dict
import unittest, unittest.mock, os, sys, ast

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import data_access
temp = data_access._get_id
data_access._get_id = unittest.mock.Mock()
#data_access = unittest.mock.Mock()
#sys.modules['data_access'] = data_access

from services.function_inference_service import FunctionClassification
from entities.Script import Script
from entities.Experiment import Experiment
from entities.FunctionGraph import FunctionGraph
from services.function_service import decorate_function

class TestFunctionService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script_graph = unittest.mock.Mock(FunctionGraph)
        cls.script_graph.get_source_code_executed = unittest.mock.Mock()

    def tearDown(self):
        files_and_folders = ['script_test.py', 
                             'script_test_2.py',
                             'folder2',
                             'folder3',
                             'folder4']
        for f in files_and_folders:
            if os.path.exists(f):
                os.system(f'rm -rf {f}')
    
    def getAST(self, nome_script:str) -> ast.Module:
        with open(nome_script, 'rt') as f:
            fileAST = ast.parse(f.read())
        return fileAST
    
    def test_decorate_global_and_inner_functions_with_collect_metadata(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n')
            f.write('def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)

        functions2code = {'f1':'def f1():\n\trandom.randint()\n',
                          'f2':'def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n',
                          'f2.<locals>.f21':'def f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n',
                          'f2.<locals>.f21.<locals>.f211':'def f211():\n\t\t\treturn "f211"\n'}
        for func in functions:
            self.script_graph.return_value = functions2code[func]
            data_access._get_id.return_value = hash(functions2code[func])
            
            self.assertEqual(len(functions[func].decorator_list), 0)
            decorate_function(functions[func], self.script_graph, {})
            self.assertEqual(functions[func].decorator_list[0].id, 'collect_metadata')
    
    def test_decorate_global_and_inner_functions_with_collect_metadata_and_deterministic(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n')
            f.write('def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)

        getId = lambda f_name: hash(ast.unparse(functions[f_name]))
        classifiedFunctions = {getId('f1'):FunctionClassification.DONT_CACHE,
                               getId('f2'):FunctionClassification.CACHE,
                               getId('f2.<locals>.f21.<locals>.f211'):FunctionClassification.DONT_CACHE}

        for func in functions:            
            self.script_graph.get_source_code_executed.return_value = ast.unparse(functions[func])
            data_access._get_id.return_value = getId(func)

            funcId = getId(func)
            self.assertEqual(len(functions[func].decorator_list), 0)
            decorate_function(functions[func], self.script_graph, classifiedFunctions)
            if funcId not in classifiedFunctions:
                self.assertEqual(functions[func].decorator_list[0].id, 'collect_metadata')
            elif classifiedFunctions[funcId] == FunctionClassification.CACHE:
                self.assertEqual(functions[func].decorator_list[0].id, 'deterministic')
            else:
                self.assertEqual(len(functions[func].decorator_list), 0)
    
    def test_dont_decorate_experiment_main_function(self):
        with open('script_test.py', 'wt') as f:
            f.write('@initialize_intpy(__file__)\ndef f1():\n\trandom.randint()\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)

        getId = lambda f_name: hash(ast.unparse(functions[f_name]))
        classifiedFunctions = {}

        self.script_graph.get_source_code_executed.return_value = ast.unparse(functions['f1'])
        data_access._get_id.return_value = getId('f1')

        self.assertEqual(len(functions['f1'].decorator_list), 1)
        decorate_function(functions['f1'], self.script_graph, classifiedFunctions)
        self.assertEqual(len(functions['f1'].decorator_list), 1)
    
if __name__ == '__main__':
    unittest.main()