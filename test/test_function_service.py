import unittest, unittest.mock, os, sys, ast

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from hashlib import md5

from services.function_inference_service import FunctionClassification
from entities.Script import Script
from entities.Experiment import Experiment
from services.function_service import decorate_function

class TestFunctionService(unittest.TestCase):
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
    
    def test_decorate_all_functions_with_collect_metadata_except_main_when_dont_exist_already_classified_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n')
            f.write('def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n')
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

        functions2hashes = {'f1':md5('def f1():\n\trandom.randint()\n'.encode('utf')),
                            'f2':md5('def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n'.encode('utf')),
                            'f2.<locals>.f21':md5('def f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n'.encode('utf')),
                            'f2.<locals>.f21.<locals>.f211':md5('def f211():\n\t\t\treturn "f211"\n'.encode('utf')),
                            'main':md5('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n'.encode('utf'))}
        
        self.assertEqual(len(functions['main'].decorator_list), 1)
        decorate_function(functions['main'], {}, functions2hashes)
        self.assertEqual(len(functions['main'].decorator_list), 1)
        for func in functions:
            if func == 'main': continue
            self.assertEqual(len(functions[func].decorator_list), 0)
            decorate_function(functions[func], {}, functions2hashes)
            self.assertEqual(len(functions[func].decorator_list), 1)
            self.assertEqual(functions[func].decorator_list[0].id, 'collect_metadata')
    
    def test_decorate_and_dont_decorate_functions_according_to_already_classified_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n')
            f.write('def f2():\n\treturn "f2"\n')
            f.write('def f3(a):\n\treturn a ** 3\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n')

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

        functions2hashes = {'f1':md5('def f1():\n\trandom.randint()\n'.encode('utf')),
                            'f2':md5('def f2():\n\treturn "f2"\n'.encode('utf')),
                            'f3':md5('def f3(a):\n\treturn a ** 3\n'.encode('utf')),
                            'main':md5('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n'.encode('utf'))}
        
        classified_functions = {functions2hashes['f1']:"CACHE",
                               functions2hashes['f2']:"DONT_CACHE",
                               functions2hashes['f3']:"MAYBE_CACHE"}
        
        self.assertEqual(len(functions['main'].decorator_list), 1)
        decorate_function(functions['main'], classified_functions, functions2hashes)
        self.assertEqual(len(functions['main'].decorator_list), 1)
        for func in functions:
            if func == 'main': continue
            self.assertEqual(len(functions[func].decorator_list), 0)
            decorate_function(functions[func], classified_functions, functions2hashes)
            
            decorator = 'collect_metadata'
            func_hash = functions2hashes[func]
            if func_hash in classified_functions:
                classification = classified_functions[func_hash]
                if classification == 'CACHE':
                    decorator = 'deterministic'
                elif classification == 'MAYBE_CACHE':
                    decorator = 'maybe_deterministic'
                else:
                    decorator = ''
            if decorator != '':
                self.assertEqual(len(functions[func].decorator_list), 1)
                self.assertEqual(functions[func].decorator_list[0].id,  decorator)
            else:
                self.assertEqual(len(functions[func].decorator_list), 0)
    
if __name__ == '__main__':
    unittest.main()