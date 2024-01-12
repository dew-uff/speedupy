import unittest, unittest.mock, os, sys, ast

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from entities.Script import Script
from entities.Experiment import Experiment
from entities.FunctionGraph import FunctionGraph

class TestFunctionGraph(unittest.TestCase):
    def tearDown(self):
        files_and_folders = ['script_test.py', 
                             'script_test_2.py',
                             'folder2',
                             'folder3',
                             'folder4']
        for f in files_and_folders:
            if os.path.exists(f):
                os.system(f'rm -rf {f}')

    def normalize_string(self, string):
        return string.replace("\n\n", "\n").replace("\t", "    ").replace("\"", "'")

    def getAST(self, nome_script:str) -> ast.Module:
        with open(nome_script, 'rt') as f:
            fileAST = ast.parse(f.read())
        return fileAST
    
    def test_get_source_code_of_function_that_doesnt_call_other_user_defined_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n\tprint(1+5)\na = input()\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        experiment.set_main_script(script)

        graph = FunctionGraph(script, [], experiment)
        code1 = graph.get_source_code_executed(functions['f1'])
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string(ast.unparse(functions['f1']))
        self.assertEqual(code1, code2)

    def test_get_source_code_of_function_that_call_other_functions_from_the_same_script(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n\tf2(10)\n\ta = input()\n\tf4(1, 2)\n')
            f.write('def f2(f):\n\tprint("f2")\n\tf3()\n\treturn f ** 2\n')
            f.write('def f3():\n\treturn "f3"\n')
            f.write('def f4(a, b):\n\treturn a + b\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f3':fileAST.body[2],
                     'f4':fileAST.body[3]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        experiment.set_main_script(script)

        graph = FunctionGraph(script, [], experiment)
        graph.add(functions['f1'], functions['f2'])
        graph.add(functions['f1'], functions['f4'])
        graph.add(functions['f2'], functions['f3'])

        code1 = graph.get_source_code_executed(functions['f1'])
        code1 = self.normalize_string(code1)
        code2 = "\n".join([ast.unparse(functions['f1']),
                           ast.unparse(functions['f2']),
                           ast.unparse(functions['f4']),
                           ast.unparse(functions['f3'])])
        code2 = self.normalize_string(code2)
        self.assertEqual(code1, code2)

    def test_get_source_code_of_function_that_call_other_functions_from_other_scripts(self):
        with open('script_test.py', 'wt') as f:
            f.write('import script_test_2\n')
            f.write('from script_test_3 import f3\n')
            f.write('def f1():\n\trandom.randint()\n\tscript_test_2.f2(10)\n\tf3()\n\tf4(1, 2)\n')
            f.write('def f4(a, b):\n\treturn a + b\n')    
        fileAST = self.getAST('script_test.py')
        imports = [fileAST.body[0], fileAST.body[1]]
        functions1 = {'f1':fileAST.body[2],
                     'f4':fileAST.body[3]}
        script1 = Script('script_test.py', fileAST, imports, functions1)

        with open('script_test_2.py', 'wt') as f:
            f.write('def f2(f):\n\tprint("f2")\n\tf21()\n')
            f.write('def f21():\n\treturn "f21"\n')
        fileAST = self.getAST('script_test_2.py')
        functions2 = {'f2':fileAST.body[0],
                     'f21':fileAST.body[1]}
        script2 = Script('script_test_2.py', fileAST, [], functions2)
        
        with open('script_test_3.py', 'wt') as f:
            f.write('def f3():\n\treturn "f3"\n')
        fileAST = self.getAST('script_test_3.py')
        functions3 = {'f3':fileAST.body[0]}
        script3 = Script('script_test_3.py', fileAST, [], functions3)
        
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script1)
        experiment.add_script(script2)
        experiment.add_script(script3)
        experiment.set_main_script(script1)

        script3_graph = FunctionGraph(script3, [], experiment)
        script3.function_graph = script3_graph

        script2_graph = FunctionGraph(script2, [], experiment)
        script2_graph.add(functions2['f2'], functions2['f21'])
        script2.function_graph = script2_graph
        
        script1_graph = FunctionGraph(script1, [script2.name, script3.name], experiment)
        script1_graph.add(functions1['f1'], functions2['f2'])
        script1_graph.add(functions1['f1'], functions3['f3'])
        script1_graph.add(functions1['f1'], functions1['f4'])

        code1 = script1_graph.get_source_code_executed(functions1['f1'])
        code1 = self.normalize_string(code1)
        code2 = "\n".join([ast.unparse(functions1['f1']),
                           ast.unparse(functions2['f2']),
                           ast.unparse(functions3['f3']),
                           ast.unparse(functions1['f4']),
                           ast.unparse(functions2['f21'])])
        code2 = self.normalize_string(code2)
        self.assertEqual(code1, code2)

    def test_get_source_code_of_recursive_function(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1(x):\n\tif x == 0:\n\t\treturn 1\n\treturn x * f1(x-1)\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        experiment.set_main_script(script)

        graph = FunctionGraph(script, [], experiment)
        graph.add(functions['f1'], functions['f1'])
        code1 = graph.get_source_code_executed(functions['f1'])
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string(ast.unparse(functions['f1']))
        self.assertEqual(code1, code2)

    def test_get_source_code_of_decorated_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1():\n\trandom.randint()\n')
            f.write('@initialize_intpy(__file__)\ndef f2(f):\n\tprint("f2")\n')
            f.write('@decorator1\n@decorator2\ndef f3():\n\treturn "f3"\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f3':fileAST.body[2]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        experiment.set_main_script(script)

        graph = FunctionGraph(script, [], experiment)

        code1 = graph.get_source_code_executed(functions['f1'])
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string('def f1():\n\trandom.randint()')
        self.assertEqual(code1, code2)

        code1 = graph.get_source_code_executed(functions['f2'])
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string('def f2(f):\n\tprint("f2")')
        self.assertEqual(code1, code2)

        code1 = graph.get_source_code_executed(functions['f3'])
        code1 = self.normalize_string(code1)
        code2 = self.normalize_string('def f3():\n\treturn "f3"')
        self.assertEqual(code1, code2)

if __name__ == '__main__':
    unittest.main()