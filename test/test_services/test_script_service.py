import unittest, unittest.mock, os, sys, ast
from unittest.mock import patch

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from services.script_service import add_start_inference_engine_import, _get_module_name
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

    def test_add_start_inference_engine_import(self):
        with open('script_test.py', 'wt') as f:
            f.write(f"import sys\nsys.path.append('{os.getcwd()}')\n")
            f.write('from speedupy.intpy import deterministic, maybe_deterministic, collect_metadata\n')
            f.write('from speedupy.intpy import execute_intpy\n')
            f.write('@deterministic\ndef f1(a, b, c=10):\n\treturn a * b / c\n')
            f.write('@maybe_deterministic\ndef f2():\n\treturn 8\n')
            f.write('@collect_metadata\ndef f3():\n\treturn "f3"\n')
            f.write('@execute_intpy\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[4],
                     'f2':fileAST.body[5],
                     'f3':fileAST.body[6],
                     'main':fileAST.body[7]}
        imports = [fileAST.body[0], fileAST.body[2], fileAST.body[3]]
        script = Script('script_test.py', fileAST, imports, functions)
        
        add_start_inference_engine_import(script)
        code1 = ast.unparse(script.AST)
        code2 = ast.unparse(script.AST).replace('from speedupy.intpy import execute_intpy\n', 'from speedupy.function_inference_engine import start_inference_engine\n')
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string(code2)
        self.assertEqual(code1, code2)

    def test_get_module_name_file_on_main_folder(self):
        script = Script('script_test.py', ast.parse(""), [], {})
        self.assertEqual(_get_module_name(script), 'script_test')

    def test_get_module_name_file_inside_subfolder(self):
        script = Script('folder1/subfolder1/script_test.py', ast.parse(""), [], {})
        self.assertEqual(_get_module_name(script), 'folder1.subfolder1.script_test')    

if __name__ == '__main__':
    unittest.main()