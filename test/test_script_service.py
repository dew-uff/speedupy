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

    def test_copy_script_with_ast_ImportFrom_commands_to_user_defined_scripts(self): pass
    def test_copy_script_with_ast_Import_commands_with_relative_path(self): pass
    def test_copy_script_with_ast_ImportFrom_commands_with_relative_path(self): pass
    
    """
    def test_copy_script(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n')
            f.write('def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0]}
        script = Script('__main__', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)

        functions2code = {'f1':'def f1():\n\trandom.randint()\n',
                          'f2':'def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n',
                          'f2.<locals>.f21':'def f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n',
                          'f2.<locals>.f21.<locals>.f211':'def f211():\n\t\t\treturn "f211"\n'}
        for func in functions:
            self.script_graph.return_value = functions2code[func]
            data_access._get_id.return_value = hash(functions2code[func])
            
            self.assertEqual(len(functions[func].decorator_list), 0)
            decorate_function(functions[func], self.script_graph, {})
            self.assertEqual(functions[func].decorator_list[0].id, 'collect_metadata')
    
    def test_decorate_global_and_inner_functions_with_collect_metadata_and_deterministic(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n')
            f.write('def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0]}
        script = Script('__main__', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)

        getId = lambda f_name: hash(ast.unparse(functions[f_name]))
        classifiedFunctions = {getId('f1'):FunctionClassification.DONT_CACHE,
                               getId('f2'):FunctionClassification.CACHE,
                               getId('f2.<locals>.f21.<locals>.f211'):FunctionClassification.DONT_CACHE}

        for func in functions:            
            self.script_graph.get_source_code_executed.return_value = ast.unparse(functions[func])
            data_access._get_id.return_value = getId(func)

            funcId = getId(func)
            self.assertEqual(len(functions[func].decorator_list), 0)
            decorate_function(functions[func], self.script_graph, classifiedFunctions)
            if funcId not in classifiedFunctions:
                self.assertEqual(functions[func].decorator_list[0].id, 'collect_metadata')
            elif classifiedFunctions[funcId] == FunctionClassification.CACHE:
                self.assertEqual(functions[func].decorator_list[0].id, 'deterministic')
            else:
                self.assertEqual(len(functions[func].decorator_list), 0)
    
    def test_dont_decorate_experiment_main_function(self):
        with open('script_test.py', 'wt') as f:
            f.write('@initialize_intpy(__file__)\ndef f1():\n\trandom.randint()\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0]}
        script = Script('__main__', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)

        getId = lambda f_name: hash(ast.unparse(functions[f_name]))
        classifiedFunctions = {}

        self.script_graph.get_source_code_executed.return_value = ast.unparse(functions['f1'])
        data_access._get_id.return_value = getId('f1')

        self.assertEqual(len(functions['f1'].decorator_list), 1)
        decorate_function(functions['f1'], self.script_graph, classifiedFunctions)
        self.assertEqual(len(functions['f1'].decorator_list), 1)
    """
if __name__ == '__main__':
    unittest.main()