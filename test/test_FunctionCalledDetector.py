from typing import List, Dict
import unittest, unittest.mock, os, sys, ast

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from entities.Script import Script
from entities.Experiment import Experiment
from services.FunctionCalledDetector import FunctionCalledDetector

class TestFunctionCalledDetector(unittest.TestCase):
    def tearDown(self):
        files_and_folders = ['script_test.py', 
                             'script_test_2.py',
                             'folder2',
                             'folder3']
        for f in files_and_folders:
            if os.path.exists(f):
                os.system(f'rm -rf {f}')

    def test_calling_non_user_defined_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('import random\nfrom os.path import exists\n')
            f.write('random.randint()\nrandom.random()\nexists("/")\n')
            f.write('print(1 + 5)\nresp = input("...")')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        script = Script('__main__', fileAST, imports, {})
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)

        self.functionCalledDetector = FunctionCalledDetector(script, experiment)
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
        script = Script('__main__', fileAST, [], {})
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)

        self.functionCalledDetector = FunctionCalledDetector(script, experiment)
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
        script1 = Script('__main__', fileAST, imports, functions)

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

        self.functionCalledDetector = FunctionCalledDetector(script1, experiment)
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
        script1 = Script('__main__', fileAST, imports, functions)

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

        self.functionCalledDetector = FunctionCalledDetector(script1, experiment)
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
        script1 = Script('__main__', fileAST, imports, functions)

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

        self.functionCalledDetector = FunctionCalledDetector(script1, experiment)
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
        script1 = Script('__main__', fileAST, imports, functions)

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

        self.functionCalledDetector = FunctionCalledDetector(script1, experiment)
        self.assertEqual(self.functionCalledDetector.find_function_called('func1'), script1.AST.body[2])
        self.assertEqual(self.functionCalledDetector.find_function_called('f2'), script2.AST.body[0])
        self.assertEqual(self.functionCalledDetector.find_function_called('st3.func3'), script3.AST.body[0])

    def test_calling_user_defined_functions_explicitly_imported_with_ast_ImportFrom_with_relative_path(self):
        os.makedirs('folder2/subfolder2')
        os.makedirs('folder3/subfolder3')
        with open('script_test.py', 'wt') as f:
            f.write('from .folder2.subfolder2.script_test_2 import func2 as f2\nfrom .folder3.subfolder3 import script_test_3 as st3\n')
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
    """
    #TODO CONTINUAR IMPLEMENTAÇÃO !!!!!!!!!
    def test_calling_user_defined_functions_implicitly_imported_with_ast_Import(self):
        os.makedirs('folder2/subfolder2')
        os.makedirs('folder3/subfolder3')
        with open('script_test.py', 'wt') as f:
            f.write('from .folder2.subfolder2.script_test_2 import func2 as f2\nfrom .folder3.subfolder3 import script_test_3 as st3\n')
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
    """
    def test_calling_user_defined_functions_implicitly_imported_with_ast_ImportFrom(self): pass
    def test_calling_user_defined_functions_implicitly_imported_with_ast_ImportFrom_with_relative_path(self): pass
    ###def test_calling_user_defined_functions_implicitly/explicitly_imported_with_ast_Import/ImportFrom_asterisk(self): pass
    def test_calling_user_defined_functions_with_the_same_name(self): pass #_global_function, inner_function and imported_function_using_as_alias
    #test_import_os_and_use_os.path.exists()


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

    def getAST(self, nome_script:str) -> ast.Module:
        with open(nome_script, 'rt') as f:
            fileAST = ast.parse(f.read())
        return fileAST

    def assert_resultados_astSearch_search(self, fileAST:ast.Module, expected_imports:List, expected_funcs:Dict[str, ast.FunctionDef]):
        astSearcher = ASTSearcher(fileAST)
        astSearcher.search()
        self.assertListEqual(astSearcher.import_commands, expected_imports)
        self.assertDictEqual(astSearcher.functions, expected_funcs)
    """
    def test_ASTSearcher_blank_file(self):
        with open('script_test.py', 'wt') as f:
            f.write('')
        
        fileAST = self.getAST('script_test.py')
        self.assert_resultados_astSearch_search(fileAST, [], {})
        os.system('rm script_test.py')

    def test_ASTSearcher_one_file_without_imports_nor_declared_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('print("abc")\nprint(1 + 3 + 5)\nresp = input("how are you?")')
        
        fileAST = self.getAST('script_test.py')
        self.assert_resultados_astSearch_search(fileAST, [], {})
        os.system('rm script_test.py')
    def test_ASTSearcher_one_file_with_only_declared_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('def func1():\n\treturn "func1"\n')
            f.write('def func2(a, b, c):\n\tprint(a * b + c)\n')
            f.write('def func3(x, y = 2):\n\treturn x ** y\n')
            f.write('func1()\nfunc2(1, -20, 3)\nfunc3(3)\nfunc3(10, y=-5)')
        
        fileAST = self.getAST('script_test.py')
        expected_funcs = {'func1': fileAST.body[0], 'func2': fileAST.body[1], 'func3': fileAST.body[2]}
        self.assert_resultados_astSearch_search(fileAST, [], expected_funcs)
        os.system('rm script_test.py')

    def test_ASTSearcher_one_file_with_only_declared_functions_and_inner_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('def func1(a, b, c):\n\tdef func11(x, y, z):\n\t\tprint(x ** y % z)\n\tfunc11(a, b, c)\n\treturn 10\n')
            f.write('def func2(a, b):\n\tdef func21(x, y, z=3):\n\t\treturn x + y % z\n\tfunc21(a, b)\n\tfunc21(a, b, z=10)\n\treturn 20\n')
            f.write('def func3():\n\tdef func31(x):\n\t\treturn x\n\tdef func32(y):\n\t\tdef func321(z):\n\t\t\tprint("func321")\n\t\t\treturn z ** 3\n\t\treturn y ** 2\n\treturn 20\n')
            
        fileAST = self.getAST('script_test.py')
        expected_funcs = {'func1': fileAST.body[0], 'func1.<locals>.func11':fileAST.body[0].body[0],
                          'func2': fileAST.body[1], 'func2.<locals>.func21':fileAST.body[1].body[0],
                          'func3': fileAST.body[2],
                          'func3.<locals>.func31':fileAST.body[2].body[0], 'func3.<locals>.func32':fileAST.body[2].body[1],
                          'func3.<locals>.func32.<locals>.func321':fileAST.body[2].body[1].body[0]}
        self.assert_resultados_astSearch_search(fileAST, [], expected_funcs)
        os.system('rm script_test.py')

    def test_ASTSearcher_one_file_with_only_declared_functions_and_classes_with_methods(self):
        with open('script_test.py', 'wt') as f:
            f.write('def func1(a, b, c):\n\tdef func11(x, y, z):\n\t\tprint(x ** y % z)\n\tfunc11(a, b, c)\n\treturn 10\n')
            f.write('class Teste1():\n\tdef __init__(self):\n\t\tself.__x = 10\n\tdef method1(self, a, b):\n\t\treturn self.__x * 2\n\tdef method2(self):\n\t\tprint("method 2")\n\t\tdef method21(x, y, z=3):\n\t\t\treturn x + y % z\n')
            f.write('class Teste2():\n\tdef __init__(self):\n\t\tself.__x = 10\n\tdef method1(self, a, b):\n\t\treturn self.__x * 2\n\tclass Teste21():\n\t\tdef __init__(self):\n\t\t\tprint("class Teste2")\n\t\tdef method3(self):\n\t\t\tprint("method 3")\n\t\t\tdef method31(a=3):\n\t\t\t\treturn a ** 6\n')
      
        fileAST = self.getAST('script_test.py')
        expected_funcs = {'func1': fileAST.body[0], 'func1.<locals>.func11':fileAST.body[0].body[0]}
        self.assert_resultados_astSearch_search(fileAST, [], expected_funcs)
        os.system('rm script_test.py')

    def test_ASTSearcher_three_files_with_explicitly_imports_and_declared_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('import script_test_2\nfrom script_test_3 import func31\n')
            f.write('def func11(a, b, c):\n\tdef func111(x, y, z):\n\t\tprint(x ** y % z)\n\tfunc111(a, b, c)\n\treturn 10\n')
            f.write('script_test_2.func21(10)\nscript_test_2.func22()\nfunc31()')
        with open('script_test_2.py', 'wt') as f:
            f.write('from script_test_3 import func31\n')
            f.write('def func21(a, b=3):\n\tdef func211():\n\t\tprint("func211")\ndef func22():\n\treturn 200\n')
            f.write('func31()')
        with open('script_test_3.py', 'wt') as f:
            f.write('def func31(x=14):\n\treturn x ** 8')
            
        fileAST = self.getAST('script_test.py')
        expected_imports = [fileAST.body[0], fileAST.body[1]]
        expected_funcs = {'func11': fileAST.body[2], 'func11.<locals>.func111':fileAST.body[2].body[0]}
        self.assert_resultados_astSearch_search(fileAST, expected_imports, expected_funcs)
        
        fileAST = self.getAST('script_test_2.py')
        expected_imports = [fileAST.body[0]]
        expected_funcs = {'func21': fileAST.body[1], 'func21.<locals>.func211':fileAST.body[1].body[0],
                          'func22': fileAST.body[2]}
        self.assert_resultados_astSearch_search(fileAST, expected_imports, expected_funcs)
        
        fileAST = self.getAST('script_test_3.py')
        expected_funcs = {'func31': fileAST.body[0]}
        self.assert_resultados_astSearch_search(fileAST, [], expected_funcs)

        os.system('rm script_test.py')
        os.system('rm script_test_2.py')
        os.system('rm script_test_3.py')
    
    def test_ASTSearcher_three_files_with_explicitly_and_implicitly_imports_and_declared_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('from . import func3\nimport script_test_2\n')
            f.write('def func1(a, b, c):\n\tdef func11(x, y, z):\n\t\tprint(x ** y % z)\n\tfunc11(a, b, c)\n\treturn 10\n')
            f.write('func1(9, -2, 3)\nfunc3(10)\nscript_test_2.func2()')
        with open('script_test_2.py', 'wt') as f:
            f.write('from . import func3\n')
            f.write('def func2(x=14):\n\treturn x ** 8\n')
            f.write('func2(x=-4)\nfunc3(7.7)')
        with open('__init__.py', 'wt') as f:
            f.write('def func3(a, b=3):\n\tdef func31():\n\t\tprint("func31")\ndef func32():\n\treturn 200\n')
        
        fileAST = self.getAST('script_test.py')
        expected_imports = [fileAST.body[0], fileAST.body[1]]
        expected_funcs = {'func1': fileAST.body[2], 'func1.<locals>.func11':fileAST.body[2].body[0]}
        self.assert_resultados_astSearch_search(fileAST, expected_imports, expected_funcs)
        
        fileAST = self.getAST('script_test_2.py')
        expected_imports = [fileAST.body[0]]
        expected_funcs = {'func2': fileAST.body[1]}
        self.assert_resultados_astSearch_search(fileAST, expected_imports, expected_funcs)
        
        fileAST = self.getAST('__init__.py')
        expected_funcs = {'func3': fileAST.body[0], 'func3.<locals>.func31':fileAST.body[0].body[0],
                          'func32': fileAST.body[1]}
        self.assert_resultados_astSearch_search(fileAST, [], expected_funcs)
        
        os.system('rm script_test.py')
        os.system('rm script_test_2.py')
        os.system('rm __init__.py')

    def test_ASTSearcher_seven_files_on_different_folders_with_explicitly_and_implicitly_imports_and_declared_functions(self):
        os.mkdir('folder2')
        os.mkdir('folder3')
        os.mkdir('folder3/subfolder3')
        with open('script_test.py', 'wt') as f:
            f.write('from . import funcInit1\nimport folder2.script_test_2\nfrom folder3.subfolder3.script_test_3 import func3\n')
            f.write('def func1(a, b, c):\n\tdef func11(x, y, z):\n\t\tprint(x ** y % z)\n\tfunc11(a, b, c)\n\treturn 10\n')
            f.write('func1(9, -2, 3)\nfuncInit1()\nfuncInit2()\nfuncInit31()\nfuncInit32()\n')
            f.write('folder2.script_test_2.func2(x=12)\nfunc3("abc")')
        with open('__init__.py', 'wt') as f:
            f.write('def funcInit1():\n\tprint("funcInit1")')
        
        with open('folder2/script_test_2.py', 'wt') as f:
            f.write('from ..folder3.subfolder3.script_test_3 import func3\n')
            f.write('def func2(x=14):\n\treturn x ** 8\n')
            f.write('func2(x=-4)\nfunc3("asd")')
        with open('folder2/__init__.py', 'wt') as f:
            f.write('def funcInit2():\n\tprint("funcInit2")\n')
        
        with open('folder3/__init__.py', 'wt') as f:
            f.write('def funcInit31():\n\tprint("funcInit31")\n')
        with open('folder3/subfolder3/script_test_3.py', 'wt') as f:
            f.write('def func3(string):\n\treturn string.upper()\n')
            f.write('func3("teste")')
        with open('folder3/subfolder3/__init__.py', 'wt') as f:
            f.write('def funcInit32():\n\tprint("funcInit32")\n')
        
        fileAST = self.getAST('script_test.py')
        expected_imports = [fileAST.body[0], fileAST.body[1], fileAST.body[2]]
        expected_funcs = {'func1': fileAST.body[3], 'func1.<locals>.func11':fileAST.body[3].body[0]}
        self.assert_resultados_astSearch_search(fileAST, expected_imports, expected_funcs)
        
        fileAST = self.getAST('__init__.py')
        expected_funcs = {'funcInit1': fileAST.body[0]}
        self.assert_resultados_astSearch_search(fileAST, [], expected_funcs)
        
        fileAST = self.getAST('folder2/script_test_2.py')
        expected_imports = [fileAST.body[0]]
        expected_funcs = {'func2': fileAST.body[1]}
        self.assert_resultados_astSearch_search(fileAST, expected_imports, expected_funcs)
        
        fileAST = self.getAST('folder2/__init__.py')
        expected_funcs = {'funcInit2': fileAST.body[0]}
        self.assert_resultados_astSearch_search(fileAST, [], expected_funcs)

        fileAST = self.getAST('folder3/__init__.py')
        expected_funcs = {'funcInit31': fileAST.body[0]}
        self.assert_resultados_astSearch_search(fileAST, [], expected_funcs)
        
        fileAST = self.getAST('folder3/subfolder3/script_test_3.py')
        expected_funcs = {'func3': fileAST.body[0]}
        self.assert_resultados_astSearch_search(fileAST, [], expected_funcs)

        fileAST = self.getAST('folder3/subfolder3/__init__.py')
        expected_funcs = {'funcInit32': fileAST.body[0]}
        self.assert_resultados_astSearch_search(fileAST, [], expected_funcs)
        
        os.system('rm -rf folder2')
        os.system('rm -rf folder3')
        os.system('rm script_test.py')
        os.system('rm __init__.py')
    """
if __name__ == '__main__':
    unittest.main()