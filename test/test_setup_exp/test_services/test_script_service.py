import unittest, unittest.mock, os, sys, ast
from unittest.mock import patch

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from setup_exp.services.script_service import decorate_script_functions, add_decorator_import, overwrite_decorated_script
from setup_exp.entities.Script import Script
from setup_exp.entities.FunctionGraph import FunctionGraph

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
                             'folder4']
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

    def assert_script_was_written_as_expected(self, expected_code:str):
        with open(self.script.name) as f:
            actual_code = f.read()
        code1 = self.normalize_string(expected_code)
        code2 = self.normalize_string(actual_code)
        self.assertEqual(code1, code2)
    
    def test_decorate_script_functions_for_execution_when_no_function_was_decorated(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1(a, b, c=10):\n\ta * b / c\n')
            f.write('@collect_metadata\ndef f2():\n\tdef f21(x, y=3):\n\t\tdef f211(a):\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_speedupy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0],
                     'main':fileAST.body[2]}
        self.script = Script('script_test.py', fileAST, [], functions)
        with patch('setup_exp.services.script_service.decorate_function', return_value=False):
            self.assertFalse(decorate_script_functions(self.script))

    def test_decorate_script_functions_for_execution_when_a_function_was_decorated(self):
        with open('script_test.py', 'wt') as f:
            f.write('@initialize_speedupy\ndef main():\n\treturn 10\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'main':fileAST.body[0]}
        self.script = Script('script_test.py', fileAST, [], functions)
        with patch('setup_exp.services.script_service.decorate_function', return_value=True):
            self.assertTrue(decorate_script_functions(self.script))

    def test_decorate_script_functions_for_execution_when_many_functions_were_decorated(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1(a, b, c=10):\n\ta * b / c\n')
            f.write('@collect_metadata\ndef f2():\n\tdef f21(x, y=3):\n\t\tdef f211(a):\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_speedupy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0],
                     'main':fileAST.body[2]}
        self.script = Script('script_test.py', fileAST, [], functions)
        with patch('setup_exp.services.script_service.decorate_function', return_value=True):
            self.assertTrue(decorate_script_functions(self.script))

    def test_overwrite_decorated_script_without_changing_its_AST(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1(a, b, c=10):\n\ta * b / c\n')
            f.write('@collect_metadata\ndef f2():\n\tdef f21(x, y=3):\n\t\tdef f211(a):\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_speedupy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        with open('script_test.py', 'rt') as f: original_script = f.read()
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0],
                     'main':fileAST.body[2]}
        self.script = Script('script_test.py', fileAST, [], functions)

        overwrite_decorated_script(self.script)
        self.assert_script_was_written_as_expected(original_script)

    def test_overwrite_decorated_script_after_changing_its_AST(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1(a, b, c=10):\n\ta * b / c\n')
            f.write('@decorator1\ndef f2():\n\tdef f21(x, y=3):\n\t\tdef f211(a):\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_speedupy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0],
                     'main':fileAST.body[2]}
        self.script = Script('script_test.py', fileAST, [], functions)
        functions['f1'].decorator_list.append(ast.Name(id='deterministic', ctx=ast.Load()))
        functions['f2'].decorator_list.append(ast.Name(id='maybe_deterministic', ctx=ast.Load()))
        functions['main'].decorator_list[0] = ast.Name(id='test', ctx=ast.Load())
                
        overwrite_decorated_script(self.script)
        expected_code = '@deterministic\ndef f1(a, b, c=10):\n\ta * b / c\n'
        expected_code += '@decorator1\n@maybe_deterministic\ndef f2():\n\tdef f21(x, y=3):\n\t\tdef f211(a):\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n'
        expected_code += '@test\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n'
        expected_code += 'main()'
        self.assert_script_was_written_as_expected(expected_code)
    
    def test_add_decorator_import_maybe_deterministic_when_script_does_not_have_this_import(self):
        with open('script_test.py', 'wt') as f:
            f.write('@maybe_deterministic\ndef f1(a, b, c=10):\n\treturn a * b / c\n')
            f.write('@maybe_deterministic\ndef f2():\n\treturn 8\n')
            f.write('@initialize_speedupy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'main':fileAST.body[2]}
        script = Script('script_test.py', fileAST, [], functions)
        
        add_decorator_import(script, 'maybe_deterministic')
        code1 = ast.unparse(script.AST.body[:3])
        code2 = f"import sys\nsys.path.append('{os.getcwd()}')\nfrom speedupy.speedupy import maybe_deterministic"
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string(code2)
        self.assertEqual(code1, code2)
    
    def test_add_decorator_import_maybe_deterministic_when_script_already_has_this_import(self):
        with open('script_test.py', 'wt') as f:
            f.write('from speedupy.speedupy import maybe_deterministic\n')
            f.write('@maybe_deterministic\ndef f1(a, b, c=10):\n\treturn a * b / c\n')
            f.write('@maybe_deterministic\ndef f2():\n\treturn 8\n')
            f.write('@initialize_speedupy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        import_commands = [fileAST.body[0]]
        functions = {'f1':fileAST.body[1],
                     'f2':fileAST.body[2],
                     'main':fileAST.body[3]}
        script = Script('script_test.py', fileAST, import_commands, functions)
        
        add_decorator_import(script, 'maybe_deterministic')
        code1 = ast.unparse(script.AST.body[:2])
        code2 = f"from speedupy.speedupy import maybe_deterministic\n@maybe_deterministic\ndef f1(a, b, c=10):\n\treturn a * b / c"
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string(code2)
        self.assertEqual(code1, code2)

    def test_add_decorator_import_initialize_speedupy_when_script_does_not_have_this_import(self):
        with open('script_test.py', 'wt') as f:
            f.write('@maybe_deterministic\ndef f1(a, b, c=10):\n\treturn a * b / c\n')
            f.write('@maybe_deterministic\ndef f2():\n\treturn 8\n')
            f.write('@initialize_speedupy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'main':fileAST.body[2]}
        script = Script('script_test.py', fileAST, [], functions)
        
        add_decorator_import(script, 'initialize_speedupy')
        code1 = ast.unparse(script.AST.body[:3])
        code2 = f"import sys\nsys.path.append('{os.getcwd()}')\nfrom speedupy.speedupy import initialize_speedupy"
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string(code2)
        self.assertEqual(code1, code2)

    def test_add_decorator_import_initialize_speedupy_when_script_already_has_this_import(self):
        with open('script_test.py', 'wt') as f:
            f.write('from speedupy.speedupy import initialize_speedupy\n')
            f.write('@maybe_deterministic\ndef f1(a, b, c=10):\n\treturn a * b / c\n')
            f.write('@maybe_deterministic\ndef f2():\n\treturn 8\n')
            f.write('@initialize_speedupy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        import_commands = [fileAST.body[0]]
        functions = {'f1':fileAST.body[1],
                     'f2':fileAST.body[2],
                     'main':fileAST.body[3]}
        script = Script('script_test.py', fileAST, import_commands, functions)
        add_decorator_import(script, 'initialize_speedupy')
        code1 = ast.unparse(script.AST.body[:2])
        code2 = f"from speedupy.speedupy import initialize_speedupy\n@maybe_deterministic\ndef f1(a, b, c=10):\n\treturn a * b / c"
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string(code2)
        self.assertEqual(code1, code2)

if __name__ == '__main__':
    unittest.main()