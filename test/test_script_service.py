import unittest, unittest.mock, os, sys, ast

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from services.script_service import copy_script, add_decorator_imports_for_execution, add_decorator_imports_for_inference
from constantes import Constantes
from entities.Script import Script
from entities.FunctionGraph import FunctionGraph


class TestScriptService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script_graph = unittest.mock.Mock(FunctionGraph)
        cls.script_graph.get_source_code_executed = unittest.mock.Mock()

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

    def assert_script_was_correctly_copied(self):
        copied_script_path = os.path.join(Constantes().TEMP_FOLDER, self.script.name)
        self.assertTrue(os.path.exists(copied_script_path))
        with open(self.script.name) as f1:
            with open(copied_script_path) as f2:
                code1 = self.normalize_string(f1.read())
                code2 = self.normalize_string(f2.read())
                self.assertEqual(code1, code2)
    
    def test_copy_script_without_changing_its_AST(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1(a, b, c=10):\n\ta * b / c\n')
            f.write('@collect_metadata\ndef f2():\n\tdef f21(x, y=3):\n\t\tdef f211(a):\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0],
                     'main':fileAST.body[2]}
        self.script = Script('script_test.py', fileAST, [], functions)
                
        copy_script(self.script)
        self.assert_script_was_correctly_copied()

    def test_copy_script_after_changing_its_AST(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1(a, b, c=10):\n\ta * b / c\n')
            f.write('@collect_metadata\ndef f2():\n\tdef f21(x, y=3):\n\t\tdef f211(a):\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0],
                     'main':fileAST.body[2]}
        script = Script('script_test.py', fileAST, [], functions)
        functions['f1'].decorator_list.append(ast.Name(id='decorator1', ctx=ast.Load()))
        functions['f2'].decorator_list.append(ast.Name(id='decorator2', ctx=ast.Load()))
        functions['main'].decorator_list[0] = ast.Name(id='execute_intpy', ctx=ast.Load())
                
        copy_script(script)
        copied_script_path = os.path.join(Constantes().TEMP_FOLDER, script.name)
        self.assertTrue(os.path.exists(copied_script_path))
        with open(copied_script_path) as f2:
            code1 = '@decorator1\ndef f1(a, b, c=10):\n\ta * b / c\n'
            code1 += '@collect_metadata\n@decorator2\ndef f2():\n\tdef f21(x, y=3):\n\t\tdef f211(a):\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n'
            code1 += '@execute_intpy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n'
            code1 += 'main()'
            code1 = self.normalize_string(code1)
            code2 = self.normalize_string(f2.read())
            self.assertEqual(code1, code2)    
    
    def test_add_decorator_imports_for_execution_to_script(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1(a, b, c=10):\n\treturn a * b / c\n')
            f.write('@maybe_deterministic\ndef f2():\n\treturn 8\n')
            f.write('@collect_metadata\ndef f3():\n\treturn "f3"\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f3':fileAST.body[2],
                     'main':fileAST.body[3]}
        script = Script('script_test.py', fileAST, [], functions)
        
        add_decorator_imports_for_execution(script)
        code1 = ast.unparse(script.AST.body[:3])
        code2 = f"import sys\nsys.path.append('{os.getcwd()}')\nfrom speedupy.intpy import execute_intpy, deterministic, maybe_deterministic, collect_metadata"
        
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string(code2)
        self.assertEqual(code1, code2)

    def test_add_decorator_imports_for_inference(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1(a, b, c=10):\n\treturn a * b / c\n')
            f.write('@maybe_deterministic\ndef f2():\n\treturn 8\n')
            f.write('@collect_metadata\ndef f3():\n\treturn "f3"\n')
            f.write('@execute_intpy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f3':fileAST.body[2],
                     'main':fileAST.body[3]}
        script = Script('script_test.py', fileAST, [], functions)
        
        add_decorator_imports_for_inference(script)
        code1 = ast.unparse(script.AST.body[:3])
        code2 = f"import sys\nsys.path.append('{os.getcwd()}')\nfrom speedupy.function_inference_engine import start_inference_engine"
        
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string(code2)
        self.assertEqual(code1, code2)

if __name__ == '__main__':
    unittest.main()