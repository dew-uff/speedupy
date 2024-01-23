import unittest, unittest.mock, os, sys, ast, importlib

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from hashlib import md5

from services.function_inference_service import FunctionClassification
from entities.Script import Script
from entities.Experiment import Experiment
from entities.Metadata import Metadata
from services.function_service import decorate_function, _get_args_and_kwargs_func_call, _get_num_executions_needed, _try_execute_func
from constantes import Constantes

class TestFunctionService(unittest.TestCase):
    def setUp(self):
        Constantes().NUM_EXEC_MIN_PARA_INFERENCIA = 20

    def tearDown(self):
        files_and_folders = ['script_test.py', 
                             'script_test_2.py',
                             'folder2',
                             'folder3',
                             'folder4']
        for f in files_and_folders:
            if os.path.exists(f):
                os.system(f'rm -rf {f}')
    
    def getAST(self, nome_script:str) -> ast.Module:
        with open(nome_script, 'rt') as f:
            fileAST = ast.parse(f.read())
        return fileAST
    
    def test_decorate_all_functions_with_collect_metadata_except_main_when_dont_exist_already_classified_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n')
            f.write('def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n')
        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f2.<locals>.f21':fileAST.body[1].body[0],
                     'f2.<locals>.f21.<locals>.f211':fileAST.body[1].body[0].body[0],
                     'main':fileAST.body[2]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        for func in functions:
            functions[func].qualname = func

        functions2hashes = {'f1':md5('def f1():\n\trandom.randint()\n'.encode('utf')),
                            'f2':md5('def f2():\n\tdef f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n\treturn "f2"\n'.encode('utf')),
                            'f2.<locals>.f21':md5('def f21():\n\t\tdef f211():\n\t\t\treturn "f211"\n\t\treturn "f21"\n'.encode('utf')),
                            'f2.<locals>.f21.<locals>.f211':md5('def f211():\n\t\t\treturn "f211"\n'.encode('utf')),
                            'main':md5('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n'.encode('utf'))}
        
        self.assertEqual(len(functions['main'].decorator_list), 1)
        decorate_function(functions['main'], {}, functions2hashes)
        self.assertEqual(len(functions['main'].decorator_list), 1)
        for func in functions:
            if func == 'main': continue
            self.assertEqual(len(functions[func].decorator_list), 0)
            decorate_function(functions[func], {}, functions2hashes)
            self.assertEqual(len(functions[func].decorator_list), 1)
            self.assertEqual(functions[func].decorator_list[0].id, 'collect_metadata')
    
    def test_decorate_and_dont_decorate_functions_according_to_already_classified_functions(self):
        with open('script_test.py', 'wt') as f:
            f.write('def f1():\n\trandom.randint()\n')
            f.write('def f2():\n\treturn "f2"\n')
            f.write('def f3(a):\n\treturn a ** 3\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n')

        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f3':fileAST.body[2],
                     'main':fileAST.body[3]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        for func in functions:
            functions[func].qualname = func

        functions2hashes = {'f1':md5('def f1():\n\trandom.randint()\n'.encode('utf')),
                            'f2':md5('def f2():\n\treturn "f2"\n'.encode('utf')),
                            'f3':md5('def f3(a):\n\treturn a ** 3\n'.encode('utf')),
                            'main':md5('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n'.encode('utf'))}
        
        classified_functions = {functions2hashes['f1']:"CACHE",
                               functions2hashes['f2']:"DONT_CACHE",
                               functions2hashes['f3']:"MAYBE_CACHE"}
        
        self.assertEqual(len(functions['main'].decorator_list), 1)
        decorate_function(functions['main'], classified_functions, functions2hashes)
        self.assertEqual(len(functions['main'].decorator_list), 1)
        for func in functions:
            if func == 'main': continue
            self.assertEqual(len(functions[func].decorator_list), 0)
            decorate_function(functions[func], classified_functions, functions2hashes)
            
            decorator = 'collect_metadata'
            func_hash = functions2hashes[func]
            if func_hash in classified_functions:
                classification = classified_functions[func_hash]
                if classification == 'CACHE':
                    decorator = 'deterministic'
                elif classification == 'MAYBE_CACHE':
                    decorator = 'maybe_deterministic'
                else:
                    decorator = ''
            if decorator != '':
                self.assertEqual(len(functions[func].decorator_list), 1)
                self.assertEqual(functions[func].decorator_list[0].id,  decorator)
            else:
                self.assertEqual(len(functions[func].decorator_list), 0)
    
    def test_dont_decorate_functions_already_decorated_by_user_when_already_classified_functions_is_empty(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1():\n\trandom.randint()\n')
            f.write('@maybe_deterministic\ndef f2():\n\treturn "f2"\n')
            f.write('@collect_metadata\ndef f3(a):\n\treturn a ** 3\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n')

        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f3':fileAST.body[2],
                     'main':fileAST.body[3]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        for func in functions:
            functions[func].qualname = func

        functions2hashes = {'f1':md5('@deterministic\ndef f1():\n\trandom.randint()\n'.encode('utf')),
                            'f2':md5('@maybe_deterministic\ndef f2():\n\treturn "f2"\n'.encode('utf')),
                            'f3':md5('@collect_metadata\ndef f3(a):\n\treturn a ** 3\n'.encode('utf')),
                            'main':md5('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n'.encode('utf'))}
        
        classified_functions = {}        
        for func in functions:
            self.assertEqual(len(functions[func].decorator_list), 1)
            old_decorator = functions[func].decorator_list[0]
            decorate_function(functions[func], classified_functions, functions2hashes)
            self.assertEqual(len(functions[func].decorator_list), 1)
            self.assertEqual(old_decorator, functions[func].decorator_list[0])
    
    def test_dont_decorate_functions_already_decorated_by_user_when_already_classified_functions_conflict_with_user_classification(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1():\n\trandom.randint()\n')
            f.write('@maybe_deterministic\ndef f2():\n\treturn "f2"\n')
            f.write('@collect_metadata\ndef f3(a):\n\treturn a ** 3\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n')

        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f3':fileAST.body[2],
                     'main':fileAST.body[3]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        for func in functions:
            functions[func].qualname = func

        functions2hashes = {'f1':md5('@deterministic\ndef f1():\n\trandom.randint()\n'.encode('utf')),
                            'f2':md5('@maybe_deterministic\ndef f2():\n\treturn "f2"\n'.encode('utf')),
                            'f3':md5('@collect_metadata\ndef f3(a):\n\treturn a ** 3\n'.encode('utf')),
                            'main':md5('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n'.encode('utf'))}
        
        classified_functions = {functions2hashes['f1']:"DONT_CACHE",
                               functions2hashes['f2']:"DONT_CACHE",
                               functions2hashes['f3']:"DONT_CACHE"}
        for func in functions:
            self.assertEqual(len(functions[func].decorator_list), 1)
            old_decorator = functions[func].decorator_list[0]
            decorate_function(functions[func], classified_functions, functions2hashes)
            self.assertEqual(len(functions[func].decorator_list), 1)
            self.assertEqual(old_decorator, functions[func].decorator_list[0])

    def test_decorate_only_functions_that_are_not_already_decorated_by_user(self):
        with open('script_test.py', 'wt') as f:
            f.write('@deterministic\ndef f1():\n\trandom.randint()\n')
            f.write('def f2():\n\treturn "f2"\n')
            f.write('def f3(a):\n\treturn a ** 3\n')
            f.write('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n')

        fileAST = self.getAST('script_test.py')
        functions = {'f1':fileAST.body[0],
                     'f2':fileAST.body[1],
                     'f3':fileAST.body[2],
                     'main':fileAST.body[3]}
        script = Script('script_test.py', fileAST, [], functions)
        experiment = Experiment(os.path.dirname(__file__))
        experiment.add_script(script)
        for func in functions:
            functions[func].qualname = func

        functions2hashes = {'f1':md5('@deterministic\ndef f1():\n\trandom.randint()\n'.encode('utf')),
                            'f2':md5('def f2():\n\treturn "f2"\n'.encode('utf')),
                            'f3':md5('def f3(a):\n\treturn a ** 3\n'.encode('utf')),
                            'main':md5('@initialize_intpy(__file__)\ndef main():\n\trandom.randint()\n'.encode('utf'))}
        
        classified_functions = {functions2hashes['f1']:"CACHE",
                               functions2hashes['f2']:"MAYBE_CACHE"}
        for func in functions:
            decorate_function(functions[func], classified_functions, functions2hashes)
            self.assertEqual(len(functions[func].decorator_list), 1)        
        self.assertEqual(functions['f1'].decorator_list[0].id, 'deterministic')
        self.assertEqual(functions['f2'].decorator_list[0].id, 'maybe_deterministic')
        self.assertEqual(functions['f3'].decorator_list[0].id, 'collect_metadata')
    
    def test_get_args_and_kwargs_func_call(self):
        args = (1, True, (1, 2), 'teste')
        kwargs = {'a':10, 'b':1.331, 'c':{'1':True}}
        metadata = [Metadata('function_hash', args, kwargs, 10, 2.3124)]
        args2, kwargs2 = _get_args_and_kwargs_func_call(metadata)
        self.assertTupleEqual(args, args2)
        self.assertDictEqual(kwargs, kwargs2)

    def test_get_num_executions_needed_when_func_need_to_be_executed(self):
        Constantes().NUM_EXEC_MIN_PARA_INFERENCIA = 20
        metadata = [Metadata('function_hash', (), {}, 10, 2.3124)]
        self.assertEqual(_get_num_executions_needed(metadata), 19)
    def test_get_num_executions_needed_when_func_executed_exactly_the_number_of_times_needed(self):
        Constantes().NUM_EXEC_MIN_PARA_INFERENCIA = 20
        metadata = [Metadata('function_hash', (), {}, 10, 2.3124) for i in range(20)]
        self.assertEqual(_get_num_executions_needed(metadata), 0)
    def test_get_num_executions_needed_when_func_executed_more_times_than_needed(self):
        Constantes().NUM_EXEC_MIN_PARA_INFERENCIA = 20
        metadata = [Metadata('function_hash', (), {}, 10, 2.3124) for i in range(30)]
        self.assertEqual(_get_num_executions_needed(metadata), 0)

    def test_try_execute_func_without_throwing_exception(self):
        global x
        x = 0
        Constantes().NUM_EXEC_MIN_PARA_INFERENCIA = 5
        metadata = [Metadata('function_hash', (), {}, 3, 2.4213) for i in range(2)]
        _try_execute_func(importlib.import_module(__name__), 'func', 'function_hash', metadata)
        self.assertEqual(x, 3)
        self.assertEqual(len(metadata), Constantes().NUM_EXEC_MIN_PARA_INFERENCIA)

    def test_try_execute_func_raising_exception_during_func_execution(self):
        Constantes().NUM_EXEC_MIN_PARA_INFERENCIA = 5
        metadata = [Metadata('function_hash', (), {}, 3, 2.4213) for i in range(2)]
        _try_execute_func(importlib.import_module(__name__), 'func_raise_exception', 'function_hash', metadata)
        self.assertEqual(len(metadata), 2)

    def test_try_execute_func_when_function_already_executed_more_times_than_necessary(self):
        global x
        x = 0
        Constantes().NUM_EXEC_MIN_PARA_INFERENCIA = 5
        metadata = [Metadata('function_hash', (), {}, 3, 2.4213) for i in range(10)]
        _try_execute_func(importlib.import_module(__name__), 'func', 'function_hash', metadata)
        self.assertEqual(x, 0)
        self.assertEqual(len(metadata), 10)

    def test_try_execute_func_when_function_executed_the_exactly_number_of_times_needed(self):
        global x
        x = 0
        Constantes().NUM_EXEC_MIN_PARA_INFERENCIA = 5
        metadata = [Metadata('function_hash', (), {}, 3, 2.4213) for i in range(5)]
        _try_execute_func(importlib.import_module(__name__), 'func', 'function_hash', metadata)
        self.assertEqual(x, 0)
        self.assertEqual(len(metadata), Constantes().NUM_EXEC_MIN_PARA_INFERENCIA)

x = 0
def func():
    global x
    x += 1

def func_raise_exception():
    raise Exception()

if __name__ == '__main__':
    unittest.main()