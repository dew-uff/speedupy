import unittest, unittest.mock, os, sys, importlib

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from constantes import Constantes
import initialize_intpy

g_argsp_no_cache = True
g_argsp_m = None

class TestInitializeIntPy(unittest.TestCase):
    def setUp(self):
        Constantes().g_argsp_m = ['2d-ad']
        Constantes().g_argsp_no_cache = False
        Constantes().g_argsp_inputs = []

    def tearDown(self):
        paths = ['.intpy/', '.intpy_temp/', 'teste.xyz', 'teste.temp', 'folder1', 'folder2']
        for p in paths:
            os.system(f'rm -rf {p}')

    def create_file(self, filename, data):
        with open(filename, 'wt') as f:
            f.write(data)
    
    def assert_files_correctly_copied_to_temp_folder(self, files):
        for f in files:
            temp_path = os.path.join(Constantes().TEMP_FOLDER, f['filename'])
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path) as temp_f:
                self.assertEqual(temp_f.read(), f['data'])
            
    def test_initialize_intpy_decorator(self):
        Constantes().g_argsp_m = None
        Constantes().g_argsp_no_cache = True
        importlib.reload(initialize_intpy)
        
        self.aux = 0
        def my_function(value):
            self.aux = value
                
        my_function(10)
        self.assertEqual(self.aux, 10)

        initialize_intpy.initialize_intpy(__file__)(my_function)(-3)
        self.assertEqual(self.aux, -3)

    def test_copy_input_when_experiment_doesnt_have_input(self):
        Constantes().g_argsp_inputs = []
        importlib.reload(initialize_intpy)
        initialize_intpy._copy_input()
        self.assertFalse(os.path.exists(Constantes().TEMP_FOLDER))

    def test_copy_input_when_experiment_has_one_input_file(self):
        files = [{'filename': 'teste.xyz', 'data': 'Arquivo de teste!\n\n'}]
        self.create_file(files[0]['filename'], files[0]['data'])
        Constantes().g_argsp_inputs = [files[0]['filename']]
        importlib.reload(initialize_intpy)
        initialize_intpy._copy_input()
        self.assert_files_correctly_copied_to_temp_folder(files)

    def test_copy_input_when_experiment_has_one_input_folder(self):
        os.mkdir('folder1/')
        files = [{'filename': 'folder1/teste1.xyz', 'data': 'Arquivo de teste1!\n\n'},
                 {'filename': 'folder1/teste2.xyz', 'data': '\n\tTestando ...\n'}]
        for f in files:
            self.create_file(f['filename'], f['data'])
        Constantes().g_argsp_inputs = ['folder1']
        importlib.reload(initialize_intpy)
        initialize_intpy._copy_input()
        self.assert_files_correctly_copied_to_temp_folder(files)

    def test_copy_input_when_experiment_has_many_input_files_and_folders(self):
        os.mkdir('folder1/')
        os.mkdir('folder2/')
        files = [{'filename': 'folder1/teste1.xyz', 'data': 'Arquivo de teste1!\n\n'},
                 {'filename': 'folder1/teste2.xyz', 'data': '\n\tTestando ...\n'},
                 {'filename': 'folder2/teste3.xyz', 'data': 'Arquivo de teste3!\n\n'},
                 {'filename': 'folder2/teste4.xyz', 'data': 'Teste 4!'},
                 {'filename': 'teste.xyz', 'data': 'Teste 5!'},
                 {'filename': 'teste.temp', 'data': 'Teste 6!\n\t\n   '}]
        for f in files:
            self.create_file(f['filename'], f['data'])
        Constantes().g_argsp_inputs = ['folder1', 'folder2/', 'teste.xyz', 'teste.temp']
        importlib.reload(initialize_intpy)
        initialize_intpy._copy_input()
        self.assert_files_correctly_copied_to_temp_folder(files)

    def test_copy_input_when_experiment_has_input_folder_with_subfolders(self):
        os.makedirs('folder1/subfolder1')
        os.makedirs('folder2/subfolder2/subsubfolder2')
        files = [{'filename': 'folder1/teste1.xyz', 'data': 'Arquivo de teste1!\n\n'},
                 {'filename': 'folder1/subfolder1/teste2.xyz', 'data': '\n\tTestando ...\n'},
                 {'filename': 'folder2/teste3.xyz', 'data': 'Arquivo de teste3!\n\n'},
                 {'filename': 'folder2/subfolder2/subsubfolder2/teste4.xyz', 'data': 'Teste 4!'}]
        for f in files:
            self.create_file(f['filename'], f['data'])
        Constantes().g_argsp_inputs = ['folder1', 'folder2/']
        importlib.reload(initialize_intpy)
        initialize_intpy._copy_input()
        self.assert_files_correctly_copied_to_temp_folder(files)

    def test_copy_input_when_experiment_has_input_file_inside_folder_and_subfolder(self):
        os.makedirs('folder1/subfolder1')
        os.makedirs('folder2/subfolder2/subsubfolder2')
        files = [{'filename': 'folder1/subfolder1/teste2.xyz', 'data': '\n\tTestando ...\n'},
                 {'filename': 'folder2/subfolder2/subsubfolder2/teste4.xyz', 'data': 'Teste 4!'}]
        for f in files:
            self.create_file(f['filename'], f['data'])
        Constantes().g_argsp_inputs = ['folder1/subfolder1/teste2.xyz',
                                       'folder2/subfolder2/subsubfolder2/teste4.xyz']
        importlib.reload(initialize_intpy)
        initialize_intpy._copy_input()
        self.assert_files_correctly_copied_to_temp_folder(files)
