import unittest, unittest.mock, os, sys, ast

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from services.script_service import copy_script
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

    
    def test_copy_script_without_import_commands(self):
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
        script = Script('script_test.py', fileAST, [], functions)
                
        copy_script(script, '')
        self.assertTrue(os.path.exists('script_test_temp.py'))
        with open('script_test.py') as f1:
            with open('script_test_temp.py') as f2:
                code1 = self.normalize_string(f1.read())
                code2 = self.normalize_string(f2.read())
                self.assertEqual(code1, code2)
        os.system('rm script_test_temp.py')

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
        script = Script('script_test.py', fileAST, imports, functions)
                
        copy_script(script, '')
        self.assertTrue(os.path.exists('script_test_temp.py'))
        with open('script_test.py') as f1:
            with open('script_test_temp.py') as f2:
                code1 = self.normalize_string(f1.read())
                code2 = self.normalize_string(f2.read())
                self.assertEqual(code1, code2)
        os.system('rm script_test_temp.py')
    
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
        script = Script('folder/subfolder/script_test.py', fileAST, imports, functions)
                
        copy_script(script, '')
        self.assertTrue(os.path.exists('folder_temp/subfolder_temp/script_test_temp.py'))
        with open('folder/subfolder/script_test.py') as f1:
            with open('folder_temp/subfolder_temp/script_test_temp.py') as f2:
                code1 = self.normalize_string(f1.read())
                code2 = self.normalize_string(f2.read())
                self.assertEqual(code1, code2)
        os.system('rm -rf folder_temp')
    
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
        script = Script('script_test.py', fileAST, imports, {})
                
        copy_script(script, '')
        self.assertTrue(os.path.exists('script_test_temp.py'))
        with open('script_test_temp.py') as f:
            code1 = self.normalize_string(f.read())
            code2 = self.normalize_string('import script_test_2_temp, script_test_3_temp as st3, folder4_temp.subfolder4_temp.script_test_4_temp')
            self.assertEqual(code1, code2)
        os.system('rm script_test_temp.py')
        
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
        script = Script('script_test.py', fileAST, imports, {})
                
        copy_script(script, '')
        self.assertTrue(os.path.exists('script_test_temp.py'))
        with open('script_test_temp.py') as f:
            code1 = self.normalize_string(f.read())
            code2 = self.normalize_string('from script_test_2_temp import f2\nfrom folder3_temp.subfolder3_temp.script_test_3_temp import f3')
            self.assertEqual(code1, code2)
        os.system('rm script_test_temp.py')
    
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
        script = Script('script_test.py', fileAST, imports, {})
        
        copy_script(script, '')
        self.assertTrue(os.path.exists('script_test_temp.py'))
        with open('script_test_temp.py') as f:
            code1 = self.normalize_string(f.read())
            code2 = self.normalize_string('from folder2_temp.subfolder2_temp import script_test_21_temp\nfrom folder2_temp.subfolder2_temp.subsubfolder2_temp import script_test_22_temp')
            self.assertEqual(code1, code2)
        os.system('rm script_test_temp.py')

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
        script = Script('folder2/subfolder2/script_test_21.py', fileAST, imports, functions)
        
        copy_script(script, '')
        self.assertTrue(os.path.exists('folder2_temp/subfolder2_temp/script_test_21_temp.py'))
        with open('folder2_temp/subfolder2_temp/script_test_21_temp.py') as f:
            code1 = self.normalize_string(f.read())
            code2 = self.normalize_string('from .. import script_test_2_temp\nfrom . import script_test_22_temp\nfrom .subsubfolder2_temp import script_test_211_temp\n@deterministic\ndef f21(a, b, c=10):\n\ta * b / c')
            self.assertEqual(code1, code2)
        os.system('rm -rf folder2_temp')
    
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
        script = Script('folder2/subfolder2/__init__.py', fileAST, [], functions)
        
        copy_script(script, '')
        self.assertTrue(os.path.exists('folder2_temp/subfolder2_temp/__init__.py'))
        with open('folder2/subfolder2/__init__.py') as f1:
            with open('folder2_temp/subfolder2_temp/__init__.py') as f2:
                code1 = self.normalize_string(f1.read())
                code2 = self.normalize_string(f2.read())
                self.assertEqual(code1, code2)
        os.system('rm -rf folder2_temp')
    """
    #TODO: IMPLEMENTAR!!!
    def test_copy_script_that_imports_other_scrips_and_reference_them_on_source_code(self):
        os.mkdir('folder3')
        with open('script_test.py', 'wt') as f:
            f.write('import script_test_2\n')
            f.write('from folder3 import script_test_3\n')
            f.write('script_test_2.f2(10, 3)\nscript_test_3.f3(10)')
        with open('script_test_2.py', 'wt') as f:
            f.write('@deterministic\ndef f2(a, b, c=10):\n\ta * b / c')
        with open('folder3/script_test_3.py', 'wt') as f:
            f.write('@collect_metadata\ndef f3(a):\n\ta * 4')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        script = Script('script_test.py', fileAST, imports, {})
        
        copy_script(script, '')
        self.assertTrue(os.path.exists('script_test_temp.py'))
        with open('script_test_temp.py') as f:
            code1 = self.normalize_string(f.read())
            code2 = self.normalize_string('import script_test_2_temp\nfrom folder3_temp import script_test_3_temp\nscript_test_2_temp.f2(10, 3)\nscript_test_3_temp.f3(10)')
            self.assertEqual(code1, code2)
        #os.system('rm script_test_temp.py')

    #TODO: IMPLEMENTAR!!!
    def test_copy_script_that_imports_other_scrips_with_alias_and_reference_them_on_source_code(self):
        os.mkdir('folder3')
        with open('script_test.py', 'wt') as f:
            f.write('import script_test_2 as st2\n')
            f.write('from folder3 import script_test_3 as st3\n')
            f.write('st2.f2(10, 3)\nst3.f3(10)')
        with open('script_test_2.py', 'wt') as f:
            f.write('@deterministic\ndef f2(a, b, c=10):\n\ta * b / c')
        with open('folder3/script_test_3.py', 'wt') as f:
            f.write('@collect_metadata\ndef f3(a):\n\ta * 4')
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        script = Script('script_test.py', fileAST, imports, {})
        
        copy_script(script, '')
        self.assertTrue(os.path.exists('script_test_temp.py'))
        with open('script_test_temp.py') as f:
            code1 = self.normalize_string(f.read())
            code2 = self.normalize_string('import script_test_2_temp\nfrom folder3_temp import script_test_3_temp\nst2.f2(10, 3)\nst3.f3(10)')
            self.assertEqual(code1, code2)
        os.system('rm script_test_temp.py')
    """

if __name__ == '__main__':
    unittest.main()