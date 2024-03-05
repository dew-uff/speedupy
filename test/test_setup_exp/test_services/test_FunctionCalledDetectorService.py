from typing import List, Dict
import unittest, unittest.mock, os, sys, ast

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from entities.Script import Script
from entities.Experiment import Experiment
from setup_exp.services.FunctionCalledDetectorService import FunctionCalledDetectorService

class TestFunctionCalledDetectorService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig_work_dir = os.getcwd()
        os.chdir(os.path.dirname(__file__))

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.orig_work_dir)
    
    def tearDown(self):
        files_and_folders = ['script_test.py', 
                             'script_test_2.py',
                             'folder2',
                             'folder3']
        for f in files_and_folders:
            if os.path.exists(f):
                os.system(f'rm -rf {f}')
    
    def getAST(self, nome_script:str) -> ast.Module:
        with open(nome_script, 'rt') as f:
            fileAST = ast.parse(f.read())
        return fileAST

    def test_calling_non_user_defined_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('import random\nfrom os.path import exists\n')
            f.write('random.randint()\nrandom.random()\nexists("/")\n')
            f.write('print(1 + 5)\nresp = input("...")')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        script = Script('script_test.py', fileAST, imports, {})
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        experiment.set_main_script(script)

        self.functionCalledDetector = FunctionCalledDetectorService(script, experiment)
        self.assertIsNone(self.functionCalledDetector.find_function_called('random.randint'))
        self.assertIsNone(self.functionCalledDetector.find_function_called('random.random'))
        self.assertIsNone(self.functionCalledDetector.find_function_called('exists'))
        self.assertIsNone(self.functionCalledDetector.find_function_called('print'))
        self.assertIsNone(self.functionCalledDetector.find_function_called('input'))
        
    def test_calling_user_defined_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('def func1():\n\tprint("func1")\n')
            f.write('def func2(a, b=3):\n\tdef func21(c):\n\t\tdef func211():\n\t\t\tprint("func211")\n\t\tfunc211()\n\t\treturn c ** 2\n\tfunc21(b)\n\treturn 10\n')
            f.write('func1()\nfunc2(1)\nfunc2(1, b=10)\n')
        fileAST = self.getAST('script_test.py')
        script = Script('script_test.py', fileAST, [], {})
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        experiment.set_main_script(script)

        self.functionCalledDetector = FunctionCalledDetectorService(script, experiment)
        self.assertIsNone(self.functionCalledDetector.find_function_called('func1'))
        self.assertIsNone(self.functionCalledDetector.find_function_called('func2'))
        self.assertIsNone(self.functionCalledDetector.find_function_called('func21'))
        self.assertIsNone(self.functionCalledDetector.find_function_called('func211'))
    
    def test_calling_user_defined_functions_explicitly_imported_with_ast_Import(self):
        os.makedirs('folder3/subfolder3')
        with open('script_test.py', 'wt') as f:
            f.write('import script_test_2\nimport folder3.subfolder3.script_test_3\n')
            f.write('def func1():\n\tprint("func1")\n')
            f.write('func1()\nscript_test_2.func2(1)\nscript_test_2.func2(1, b=10)\nfolder3.subfolder3.script_test_3.func3(10)')        
        with open('script_test_2.py', 'wt') as f:
            f.write('def func2(a, b=3):\n\tdef func21(c):\n\t\tdef func211():\n\t\t\tprint("func211")\n\t\tfunc211()\n\t\treturn c ** 2\n\tfunc21(b)\n\treturn 10\n')
        with open('folder3/subfolder3/script_test_3.py', 'wt') as f:
            f.write('def func3(x):\n\tdef func31():\n\t\tprint("func31")\n\tfunc31()\n\treturn x ** 2\n')
        
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        functions = {'func1':fileAST.body[2]}
        script1 = Script('script_test.py', fileAST, imports, functions)

        fileAST = self.getAST('script_test_2.py')
        functions = {'func2':fileAST.body[0],
                     'func2.<locals>.func21':fileAST.body[0].body[0],
                     'func2.<locals>.func21.<locals>.func211':fileAST.body[0].body[0].body[0]}
        script2 = Script('script_test_2.py', fileAST, [], functions)

        fileAST = self.getAST('folder3/subfolder3/script_test_3.py')
        functions = {'func3':fileAST.body[0],
                     'func3.<locals>.func31':fileAST.body[0].body[0]}
        script3 = Script('folder3/subfolder3/script_test_3.py', fileAST, [], functions)

        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script1)
        experiment.add_script(script2)
        experiment.add_script(script3)
        experiment.set_main_script(script1)

        self.functionCalledDetector = FunctionCalledDetectorService(script1, experiment)
        self.assertEqual(self.functionCalledDetector.find_function_called('func1'), script1.AST.body[2])
        self.assertEqual(self.functionCalledDetector.find_function_called('script_test_2.func2'), script2.AST.body[0])
        self.assertEqual(self.functionCalledDetector.find_function_called('folder3.subfolder3.script_test_3.func3'), script3.AST.body[0])

    def test_calling_user_defined_functions_explicitly_imported_with_ast_ImportFrom(self):
        os.makedirs('folder3/subfolder3')
        with open('script_test.py', 'wt') as f:
            f.write('from script_test_2 import func2\nfrom folder3.subfolder3 import script_test_3\n')
            f.write('def func1():\n\tprint("func1")\n')
            f.write('func1()\nfunc2(1)\nfunc2(1, b=10)\nscript_test_3.func3(10)')
        with open('script_test_2.py', 'wt') as f:
            f.write('def func2(a, b=3):\n\tdef func21(c):\n\t\tdef func211():\n\t\t\tprint("func211")\n\t\tfunc211()\n\t\treturn c ** 2\n\tfunc21(b)\n\treturn 10\n')
        with open('folder3/subfolder3/script_test_3.py', 'wt') as f:
            f.write('def func3(x):\n\tdef func31():\n\t\tprint("func31")\n\tfunc31()\n\treturn x ** 2\n')
        
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        functions = {'func1':fileAST.body[2]}
        script1 = Script('script_test.py', fileAST, imports, functions)

        fileAST = self.getAST('script_test_2.py')
        functions = {'func2':fileAST.body[0],
                     'func2.<locals>.func21':fileAST.body[0].body[0],
                     'func2.<locals>.func21.<locals>.func211':fileAST.body[0].body[0].body[0]}
        script2 = Script('script_test_2.py', fileAST, [], functions)

        fileAST = self.getAST('folder3/subfolder3/script_test_3.py')
        functions = {'func3':fileAST.body[0],
                     'func3.<locals>.func31':fileAST.body[0].body[0]}
        script3 = Script('folder3/subfolder3/script_test_3.py', fileAST, [], functions)

        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script1)
        experiment.add_script(script2)
        experiment.add_script(script3)
        experiment.set_main_script(script1)

        self.functionCalledDetector = FunctionCalledDetectorService(script1, experiment)
        self.assertEqual(self.functionCalledDetector.find_function_called('func1'), script1.AST.body[2])
        self.assertEqual(self.functionCalledDetector.find_function_called('func2'), script2.AST.body[0])
        self.assertEqual(self.functionCalledDetector.find_function_called('script_test_3.func3'), script3.AST.body[0])
    
    def test_calling_user_defined_functions_explicitly_imported_with_ast_Import_using_as_alias(self):
        os.makedirs('folder3/subfolder3')
        with open('script_test.py', 'wt') as f:
            f.write('import script_test_2 as st2\nimport folder3.subfolder3.script_test_3 as st3\n')
            f.write('def func1():\n\tprint("func1")\n')
            f.write('func1()\nst2.func2(1)\nst2.func2(1, b=10)\nst3.func3(10)')        
        with open('script_test_2.py', 'wt') as f:
            f.write('def func2(a, b=3):\n\tdef func21(c):\n\t\tdef func211():\n\t\t\tprint("func211")\n\t\tfunc211()\n\t\treturn c ** 2\n\tfunc21(b)\n\treturn 10\n')
        with open('folder3/subfolder3/script_test_3.py', 'wt') as f:
            f.write('def func3(x):\n\tdef func31():\n\t\tprint("func31")\n\tfunc31()\n\treturn x ** 2\n')
        
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        functions = {'func1':fileAST.body[2]}
        script1 = Script('script_test.py', fileAST, imports, functions)

        fileAST = self.getAST('script_test_2.py')
        functions = {'func2':fileAST.body[0],
                     'func2.<locals>.func21':fileAST.body[0].body[0],
                     'func2.<locals>.func21.<locals>.func211':fileAST.body[0].body[0].body[0]}
        script2 = Script('script_test_2.py', fileAST, [], functions)

        fileAST = self.getAST('folder3/subfolder3/script_test_3.py')
        functions = {'func3':fileAST.body[0],
                     'func3.<locals>.func31':fileAST.body[0].body[0]}
        script3 = Script('folder3/subfolder3/script_test_3.py', fileAST, [], functions)

        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script1)
        experiment.add_script(script2)
        experiment.add_script(script3)
        experiment.set_main_script(script1)

        self.functionCalledDetector = FunctionCalledDetectorService(script1, experiment)
        self.assertEqual(self.functionCalledDetector.find_function_called('func1'), script1.AST.body[2])
        self.assertEqual(self.functionCalledDetector.find_function_called('st2.func2'), script2.AST.body[0])
        self.assertEqual(self.functionCalledDetector.find_function_called('st3.func3'), script3.AST.body[0])
    
    def test_calling_user_defined_functions_explicitly_imported_with_ast_ImportFrom_using_as_alias(self):
        os.makedirs('folder3/subfolder3')
        with open('script_test.py', 'wt') as f:
            f.write('from script_test_2 import func2 as f2\nfrom folder3.subfolder3 import script_test_3 as st3\n')
            f.write('def func1():\n\tprint("func1")\n')
            f.write('func1()\nf2(1)\nf2(1, b=10)\nst3.func3(10)')
        with open('script_test_2.py', 'wt') as f:
            f.write('def func2(a, b=3):\n\tdef func21(c):\n\t\tdef func211():\n\t\t\tprint("func211")\n\t\tfunc211()\n\t\treturn c ** 2\n\tfunc21(b)\n\treturn 10\n')
        with open('folder3/subfolder3/script_test_3.py', 'wt') as f:
            f.write('def func3(x):\n\tdef func31():\n\t\tprint("func31")\n\tfunc31()\n\treturn x ** 2\n')
        
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        functions = {'func1':fileAST.body[2]}
        script1 = Script('script_test.py', fileAST, imports, functions)

        fileAST = self.getAST('script_test_2.py')
        functions = {'func2':fileAST.body[0],
                     'func2.<locals>.func21':fileAST.body[0].body[0],
                     'func2.<locals>.func21.<locals>.func211':fileAST.body[0].body[0].body[0]}
        script2 = Script('script_test_2.py', fileAST, [], functions)

        fileAST = self.getAST('folder3/subfolder3/script_test_3.py')
        functions = {'func3':fileAST.body[0],
                     'func3.<locals>.func31':fileAST.body[0].body[0]}
        script3 = Script('folder3/subfolder3/script_test_3.py', fileAST, [], functions)

        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script1)
        experiment.add_script(script2)
        experiment.add_script(script3)
        experiment.set_main_script(script1)

        self.functionCalledDetector = FunctionCalledDetectorService(script1, experiment)
        self.assertEqual(self.functionCalledDetector.find_function_called('func1'), script1.AST.body[2])
        self.assertEqual(self.functionCalledDetector.find_function_called('f2'), script2.AST.body[0])
        self.assertEqual(self.functionCalledDetector.find_function_called('st3.func3'), script3.AST.body[0])

    def test_calling_user_defined_functions_explicitly_imported_with_ast_ImportFrom_with_relative_path(self):
        os.makedirs('folder2/subfolder2/subsubfolder2/subsubsubfolder2')
        with open('script_test.py', 'wt') as f:
            f.write('from folder2.subfolder2.subsubfolder2.script_test_subsub2 import funcsubsub2 as f2sub2\n')
            f.write('f2sub2(1)\nf2sub2(1, b=10)')
        with open('folder2/subfolder2/subsubfolder2/script_test_subsub2.py', 'wt') as f:
            f.write('from .subsubsubfolder2.script_test_subsubsub2 import funcsubsubsub2 as f3sub2\n')
            f.write('from ..script_test_sub2 import funcsub2 as fsub2\n')
            f.write('from ...script_test_2 import func2 as f2\n')
            f.write('def funcsubsub2(a, b=3):\n\treturn 10\n')
            f.write('f2("teste3")\nfsub2("teste2")\nf3sub2("teste1")')
        with open('folder2/script_test_2.py', 'wt') as f:
            f.write('def func2(text):\n\treturn text.upper()')
        with open('folder2/subfolder2/script_test_sub2.py', 'wt') as f:
            f.write('def funcsub2(msg):\n\treturn msg.title()\n')
        with open('folder2/subfolder2/subsubfolder2/subsubsubfolder2/script_test_subsubsub2.py', 'wt') as f:
            f.write('def funcsubsubsub2(msg):\n\treturn msg.find(".")\n')
        
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0]]
        script1 = Script('script_test.py', fileAST, imports, {})

        fileAST = self.getAST('folder2/script_test_2.py')
        functions = {'func2':fileAST.body[0]}
        script2 = Script('folder2/script_test_2.py', fileAST, [], functions)

        fileAST = self.getAST('folder2/subfolder2/script_test_sub2.py')
        functions = {'funcsub2':fileAST.body[0]}
        scriptsub2 = Script('folder2/subfolder2/script_test_sub2.py', fileAST, [], functions)

        fileAST = self.getAST('folder2/subfolder2/subsubfolder2/script_test_subsub2.py')
        imports = [fileAST.body[0], fileAST.body[1], fileAST.body[2]]
        functions = {'funcsubsub2':fileAST.body[3]}
        scriptsubsub2 = Script('folder2/subfolder2/subsubfolder2/script_test_subsub2.py', fileAST, imports, functions)

        fileAST = self.getAST('folder2/subfolder2/subsubfolder2/subsubsubfolder2/script_test_subsubsub2.py')
        functions = {'funcsubsubsub2':fileAST.body[0]}
        scriptsubsubsub2 = Script('folder2/subfolder2/subsubfolder2/subsubsubfolder2/script_test_subsubsub2.py', fileAST, [], functions)

        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script1)
        experiment.add_script(script2)
        experiment.add_script(scriptsub2)
        experiment.add_script(scriptsubsub2)
        experiment.add_script(scriptsubsubsub2)
        experiment.set_main_script(script1)

        self.functionCalledDetector = FunctionCalledDetectorService(scriptsubsub2, experiment)
        self.assertEqual(self.functionCalledDetector.find_function_called('f2'), script2.AST.body[0])
        self.assertEqual(self.functionCalledDetector.find_function_called('fsub2'), scriptsub2.AST.body[0])
        self.assertEqual(self.functionCalledDetector.find_function_called('f3sub2'), scriptsubsubsub2.AST.body[0])
    """
    #TODO CONTINUAR IMPLEMENTAÇÃO !!!!!!!!!
    def test_calling_user_defined_functions_implicitly_imported_with_ast_Import(self):
        os.makedirs('folder3/subfolder3')
        with open('script_test.py', 'wt') as f:
            f.write('import folder3\nfrom .folder3.subfolder3 import script_test_3 as st3\n')
            f.write('def func1():\n\tprint("func1")\n')
            f.write('func1()\nf2(1)\nf2(1, b=10)\nst3.func3(10)')
        with open('folder2/subfolder2/script_test_2.py', 'wt') as f:
            f.write('from ....folder3.subfolder3.script_test_3 import func3 as f3\n')
            f.write('def func2(a, b=3):\n\tdef func21(c):\n\t\tdef func211():\n\t\t\tprint("func211")\n\t\tfunc211()\n\t\treturn c ** 2\n\tfunc21(b)\n\treturn 10\n')
            f.write('f3("teste1")\nf3("teste2")\n')
        with open('folder3/subfolder3/script_test_3.py', 'wt') as f:
            f.write('def func3(x):\n\tdef func31():\n\t\tprint("func31")\n\tfunc31()\n\treturn x ** 2\n')
        
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        functions = {'func1':fileAST.body[2]}
        script1 = Script('__main__', fileAST, imports, functions)

        fileAST = self.getAST('folder2/subfolder2/script_test_2.py')
        imports = [fileAST.body[0]]
        functions = {'func2':fileAST.body[1],
                     'func2.<locals>.func21':fileAST.body[1].body[0],
                     'func2.<locals>.func21.<locals>.func211':fileAST.body[1].body[0].body[0]}
        script2 = Script('folder2/subfolder2/script_test_2.py', fileAST, imports, functions)

        fileAST = self.getAST('folder3/subfolder3/script_test_3.py')
        functions = {'func3':fileAST.body[0],
                     'func3.<locals>.func31':fileAST.body[0].body[0]}
        script3 = Script('folder3/subfolder3/script_test_3.py', fileAST, [], functions)

        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script1)
        experiment.add_script(script2)
        experiment.add_script(script3)

        self.functionCalledDetector = FunctionCalledDetector(script1, experiment)
        self.assertEqual(self.functionCalledDetector.find_function_called('func1'), script1.AST.body[2])
        self.assertEqual(self.functionCalledDetector.find_function_called('f2'), script2.AST.body[1])
        self.assertEqual(self.functionCalledDetector.find_function_called('st3.func3'), script3.AST.body[0])
        self.functionCalledDetector = FunctionCalledDetector(script2, experiment)
        self.assertEqual(self.functionCalledDetector.find_function_called('f3'), script3.AST.body[0])
    
    def test_calling_user_defined_functions_implicitly_imported_with_ast_ImportFrom(self): pass
    def test_calling_user_defined_functions_implicitly_imported_with_ast_ImportFrom_with_relative_path(self): pass
    ###def test_calling_user_defined_functions_implicitly/explicitly_imported_with_ast_Import/ImportFrom_asterisk(self): pass
    def test_calling_user_defined_functions_with_the_same_name(self): pass #_global_function, inner_function and imported_function_using_as_alias
    #test_import_os_and_use_os.path.exists()
    """

    """
    SCRIPT
    def __init__(self, name = "", AST = None, import_commands = set(), functions = {}, function_graph = None):
        self.__name = name
        self.__AST = AST
        self.__import_commands = import_commands
        self.__functions = functions
        self.__function_graph = function_graph

    EXPERIMENT
    def __init__(self, experiment_base_dir):
        self.__base_dir = experiment_base_dir
        self.__scripts = {}

    def add_script(self, script):
        self.__scripts[script.name] = script
    



    def __init__(self, script:Script, experiment:Experiment):
        self.__script = script
        self.__experiment = experiment
    
    def find_function_called(self, function_called_name:str):
        self.__function_called_name = function_called_name
        self.__find_possible_functions_called()
        self.__find_which_function_was_called()
        return self.__function_called
    """
    
if __name__ == '__main__':
    unittest.main()