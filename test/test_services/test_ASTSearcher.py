from typing import List, Dict
import unittest, unittest.mock, os, sys, ast

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from services.ASTSearcher import ASTSearcher

class TestASTSearcher(unittest.TestCase):
    def getAST(self, nome_script:str) -> ast.Module:
        with open(nome_script, 'rt') as f:
            fileAST = ast.parse(f.read())
        return fileAST

    def assert_resultados_astSearch_search(self, fileAST:ast.Module, expected_imports:List, expected_funcs:Dict[str, ast.FunctionDef]):
        astSearcher = ASTSearcher(fileAST)
        astSearcher.search()
        self.assertListEqual(astSearcher.import_commands, expected_imports)
        self.assertDictEqual(astSearcher.functions, expected_funcs)
    
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

if __name__ == '__main__':
    unittest.main()