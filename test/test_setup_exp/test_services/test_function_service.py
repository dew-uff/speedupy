import unittest, os, sys, ast, importlib
from unittest.mock import patch

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from hashlib import md5

from entities.Script import Script
from entities.Experiment import Experiment
from entities.Metadata import Metadata
from setup_exp.services.function_service import decorate_main_function, decorate_function
from constantes import Constantes

class TestFunctionService(unittest.TestCase):
    def setUp(self):
        Constantes().MAX_ERROR_RATE = 0.2
        Constantes().NUM_EXEC_MIN_PARA_INFERENCIA = 20
        Constantes().MIN_TIME_TO_CACHE = 1
        Constantes().MIN_TIME_TO_SIMULATE_FUNC_CALL = 10

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
    
    def test_decorate_main_function_when_it_is_not_decorated(self):
        with open('script_test.py', 'wt') as f:
            f.write('def main():\n\trandom.randint()\n')
        fileAST = self.getAST('script_test.py')
        functions = {'main':fileAST.body[0]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        for func in functions:
            functions[func].qualname = func
        
        self.assertEqual(len(functions['main'].decorator_list), 0)
        decorate_main_function(functions['main'])
        self.assertEqual(len(functions['main'].decorator_list), 1)
        self.assertEqual(functions[func].decorator_list[0].id, 'initialize_speedupy')

    def test_decorate_main_function_when_it_is_already_decorated(self):
        with open('script_test.py', 'wt') as f:
            f.write('@initialize_speedupy\ndef main():\n\trandom.randint()\n')
        fileAST = self.getAST('script_test.py')
        functions = {'main':fileAST.body[0]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        for func in functions:
            functions[func].qualname = func
        
        self.assertEqual(len(functions['main'].decorator_list), 1)
        decorate_main_function(functions['main'])
        self.assertEqual(len(functions['main'].decorator_list), 1)
        self.assertEqual(functions[func].decorator_list[0].id, 'initialize_speedupy')

    def test_decorate_function_all_functions_except_main(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n')
            f.write('def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_speedupy\ndef main():\n\trandom.randint()\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0],
                     'main':fileAST.body[2]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        for func in functions:
            functions[func].qualname = func
        
        self.assertEqual(len(functions['main'].decorator_list), 1)
        self.assertFalse(decorate_function(functions['main']))
        self.assertEqual(len(functions['main'].decorator_list), 1)
        for func in functions:
            if func == 'main': continue
            self.assertEqual(len(functions[func].decorator_list), 0)
            self.assertTrue(decorate_function(functions[func]))
            self.assertEqual(len(functions[func].decorator_list), 1)
            self.assertEqual(functions[func].decorator_list[0].id, 'maybe_deterministic')
    
    def test_dont_decorate_functions_already_decorated_by_the_user(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1():\n\trandom.randint()\n')
            f.write('@maybe_deterministic\ndef f2():\n\treturn "f2"\n')
            f.write('@deterministic\ndef f3(a):\n\treturn a ** 3\n')
            f.write('@initialize_speedupy\ndef main():\n\trandom.randint()\n')

        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f3':fileAST.body[2],
                     'main':fileAST.body[3]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        for func in functions:
            functions[func].qualname = func
              
        for func in functions:
            self.assertEqual(len(functions[func].decorator_list), 1)
            old_decorator = functions[func].decorator_list[0]
            self.assertFalse(decorate_function(functions[func]))
            self.assertEqual(len(functions[func].decorator_list), 1)
            self.assertEqual(old_decorator, functions[func].decorator_list[0])
    
    def test_decorate_only_functions_that_are_not_already_decorated_by_the_user(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1():\n\trandom.randint()\n')
            f.write('def f2():\n\treturn "f2"\n')
            f.write('def f3(a):\n\treturn a ** 3\n')
            f.write('@initialize_speedupy\ndef main():\n\trandom.randint()\n')

        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f3':fileAST.body[2],
                     'main':fileAST.body[3]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        for func in functions:
            functions[func].qualname = func

        for func in functions:
            ret = decorate_function(functions[func])
            self.assertEqual(len(functions[func].decorator_list), 1)
            if func in ['f1', 'main']:
                self.assertFalse(ret)
                continue
            else: self.assertTrue(ret)
            self.assertEqual(functions[func].decorator_list[0].id, 'maybe_deterministic')
        self.assertEqual(functions['f1'].decorator_list[0].id, 'deterministic')
        self.assertEqual(functions['main'].decorator_list[0].id, 'initialize_speedupy')

x = 0
def func():
    global x
    x += 1

if __name__ == '__main__':
    unittest.main()