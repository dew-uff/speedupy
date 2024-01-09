import unittest, unittest.mock, os, sys, ast

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

sys.modules['script_service'] = unittest.mock.Mock()
sys.modules['script_service'].decorate_script_functions = unittest.mock.Mock()

from services import experiment_service
from entities.Script import Script
from entities.Experiment import Experiment
from entities.FunctionGraph import FunctionGraph


class TestExperimentService(unittest.TestCase):
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

    # def assert_script_was_correctly_copied(self):
    #     copied_script_path = os.path.join(TEMP_FOLDER, self.script.name)
    #     self.assertTrue(os.path.exists(copied_script_path))
    #     with open(self.script.name) as f1:
    #         with open(copied_script_path) as f2:
    #             code1 = self.normalize_string(f1.read())
    #             code2 = self.normalize_string(f2.read())
    #             self.assertEqual(code1, code2)
    
    def test_decorate_experiment_main_function(self):
        with open('script_test.py', 'wt') as f:
            f.write('import random, os, sys\nfrom matplotlib import pyplot as plt\n')
            f.write('from speedupy.intpy import initialize_intpy\n')
            f.write('@decorator1\n@decorator2(__file__)\ndef f1():\n\treturn "f1"\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\tf1(1, 2, 3)\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1], fileAST.body[2]]
        functions = {'f1':fileAST.body[3],
                     'main':fileAST.body[4]}
        script = Script('script_test.py', fileAST, imports, functions)
        experiment = Experiment('')
        experiment.add_script(script)

        

        experiment_service.decorate_experiment_functions(experiment)
        
        with open(script.name) as f1:
            code1 = 'import sys\nsys.path.append(/home/joaolopez/Downloads)\nfrom speedupy.intpy import execute_intpy' + f1.read().replace('@initialize_intpy', '@execute_intpy')
            code2 = ast.unparse(script.AST)
            code1 = self.normalize_string(code1)
            code2 = self.normalize_string(code2)
            self.assertEqual(code1, code2)
        ##########self.assert_script_was_correctly_copied()
    """
    def test_copy_script_with_import_commands_to_non_user_defined_scripts(self):
        with open('script_test.py', 'wt') as f:
            f.write('import random, os, sys\nfrom matplotlib.pyplot import *\n')
            f.write('@deterministic\ndef f1(a, b, c=10):\n\ta * b / c\n')
            f.write('@collect_metadata\ndef f2():\n\tdef f21(x, y=3):\n\t\tdef f211(a):\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        functions = {'f1':fileAST.body[2],
                     'f2':fileAST.body[3],
                     'f2.<locals>.f21':fileAST.body[3].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[3].body[0].body[0],
                     'main':fileAST.body[4]}
        self.script = Script('script_test.py', fileAST, imports, functions)
                
        copy_script(self.script)
        self.assert_script_was_correctly_copied()
    
    def test_copy_script_which_is_inside_a_folder(self):
        os.makedirs('folder/subfolder')
        with open('folder/subfolder/script_test.py', 'wt') as f:
            f.write('import random, os, sys\nfrom matplotlib.pyplot import *\n')
            f.write('@deterministic\ndef f1(a, b, c=10):\n\ta * b / c\n')
            f.write('@collect_metadata\ndef f2():\n\tdef f21(x, y=3):\n\t\tdef f211(a):\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\tf1(1, 2, 3)\n\tf2()\n')
            f.write('main()')
        fileAST = self.getAST('folder/subfolder/script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        functions = {'f1':fileAST.body[2],
                     'f2':fileAST.body[3],
                     'f2.<locals>.f21':fileAST.body[3].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[3].body[0].body[0],
                     'main':fileAST.body[4]}
        self.script = Script('folder/subfolder/script_test.py', fileAST, imports, functions)
                
        copy_script(self.script)
        self.assert_script_was_correctly_copied()
    
    def test_copy_script_with_ast_Import_commands_to_user_defined_scripts(self):
        os.makedirs('folder4/subfolder4')
        with open('script_test.py', 'wt') as f:
            f.write('import script_test_2, script_test_3 as st3, folder4.subfolder4.script_test_4')
        with open('script_test_2.py', 'wt') as f:
            f.write('@deterministic\ndef f2(a, b, c=10):\n\ta * b / c\n')
        with open('script_test_3.py', 'wt') as f:
            f.write('@collect_metadata\ndef f3():\n\treturn "f3"\n')
        with open('folder4/subfolder4/script_test_4.py', 'wt') as f:
            f.write('@collect_metadata\ndef f4():\n\tpass')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0]]
        self.script = Script('script_test.py', fileAST, imports, {})
                
        copy_script(self.script)
        self.assert_script_was_correctly_copied()

    def test_copy_script_with_ast_ImportFrom_commands_to_user_defined_functions(self):
        os.makedirs('folder3/subfolder3')
        with open('script_test.py', 'wt') as f:
            f.write('from script_test_2 import f2\n')
            f.write('from folder3.subfolder3.script_test_3 import f3')
        with open('script_test_2.py', 'wt') as f:
            f.write('@deterministic\ndef f2(a, b, c=10):\n\ta * b / c\n')
        with open('folder3/subfolder3/script_test_3.py', 'wt') as f:
            f.write('@collect_metadata\ndef f3():\n\treturn "f3"\n')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        self.script = Script('script_test.py', fileAST, imports, {})
                
        copy_script(self.script)
        self.assert_script_was_correctly_copied()
    
    def test_copy_script_with_ast_ImportFrom_commands_to_user_defined_scripts(self):
        os.makedirs('folder2/subfolder2/subsubfolder2')
        with open('script_test.py', 'wt') as f:
            f.write('from folder2.subfolder2 import script_test_21\n')
            f.write('from folder2.subfolder2.subsubfolder2 import script_test_22')
        with open('folder2/subfolder2/script_test_21.py', 'wt') as f:
            f.write('@deterministic\ndef f2(a, b, c=10):\n\ta * b / c\n')
        with open('folder2/subfolder2/subsubfolder2/script_test_22.py', 'wt') as f:
            f.write('@collect_metadata\ndef f3():\n\treturn "f3"\n')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        self.script = Script('script_test.py', fileAST, imports, {})
        
        copy_script(self.script)
        self.assert_script_was_correctly_copied()

    def test_copy_script_with_ast_ImportFrom_commands_with_relative_path(self):
        os.makedirs('folder2/subfolder2/subsubfolder2')
        with open('script_test.py', 'wt') as f:
            f.write('import folder2.subfolder2.script_test_21\n')
        with open('folder2/subfolder2/script_test_21.py', 'wt') as f:
            f.write('from .. import script_test_2\n')
            f.write('from . import script_test_22\n')
            f.write('from .subsubfolder2 import script_test_211\n')
            f.write('@deterministic\ndef f21(a, b, c=10):\n\ta * b / c\n')
        with open('folder2/script_test_2.py', 'wt') as f:
            f.write('@deterministic\ndef f2(a):\n\ta ** 7\n')
        with open('folder2/subfolder2/script_test_22.py', 'wt') as f:
            f.write('@collect_metadata\ndef f22():\n\treturn "f22"\n')
        with open('folder2/subfolder2/subsubfolder2/script_test_211.py', 'wt') as f:
            f.write('@collect_metadata\ndef f211():\n\treturn "f211"\n')
        
        fileAST = self.getAST('folder2/subfolder2/script_test_21.py')
        imports = [fileAST.body[0], fileAST.body[1], fileAST.body[2]]
        functions = {"f21": fileAST.body[3]}
        self.script = Script('folder2/subfolder2/script_test_21.py', fileAST, imports, functions)
        
        copy_script(self.script)
        self.assert_script_was_correctly_copied()
    
    def test_copy_script_that_is_implicitly_imported_by_other_scripts(self):
        os.makedirs('folder2/subfolder2/subsubfolder2')
        with open('script_test.py', 'wt') as f:
            f.write('import folder2.subfolder2.script_test_21\n')
        with open('folder2/subfolder2/script_test_21.py', 'wt') as f:
            f.write('@deterministic\ndef f21(a, b, c=10):\n\ta * b / c\n')
        with open('folder2/subfolder2/__init__.py', 'wt') as f:
            f.write('@deterministic\ndef finit21(a, b, c=10):\n\ta * b / c')
        fileAST = self.getAST('folder2/subfolder2/__init__.py')
        functions = {'finit21':fileAST.body[0]}
        self.script = Script('folder2/subfolder2/__init__.py', fileAST, [], functions)
        
        copy_script(self.script)
        self.assert_script_was_correctly_copied()
    """
if __name__ == '__main__':
    unittest.main()