import unittest, unittest.mock, os, sys, copy

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import os
from banco import Banco
from data_access import get_already_classified_functions, CONEXAO_BANCO

class TestDataAccess(unittest.TestCase):
    def setUp(self):
        global CONEXAO_BANCO
        os.system("rm .intpy_test.db")
        self.conexaoBanco = Banco(".intpy_test.db")
        stmt = "CREATE TABLE IF NOT EXISTS CLASSIFIED_FUNCTIONS (\
        id INTEGER PRIMARY KEY AUTOINCREMENT,\
        function_hash TEXT NOT NULL,\
        classification TEXT NOT NULL\
        );"
        self.conexaoBanco.executarComandoSQLSemRetorno(stmt)
        CONEXAO_BANCO = self.conexaoBanco

    def tearDown(self):
        os.system("rm .intpy_test.db")

    def test_get_already_classified_functions_many_functions(self):
        f1 = hash('def f1():\n\treturn "f1"')
        f2 = hash('def f2(a):\n\treturn a ** 2')
        f3 = hash('def f3(x, y):\n\treturn x/y')
        f4 = hash('def f4():\n\treturn "f4"')
        self.conexaoBanco.executarComandoSQLSemRetorno(f"INSERT INTO CLASSIFIED_FUNCTIONS(function_hash, classification) VALUES ('{f1}', 'CACHE'), ('{f2}', 'CACHE'), ('{f3}', 'DONT_CACHE'), ('{f4}', 'DONT_CACHE');")

        functions = get_already_classified_functions()
        self.assertDictEqual({f1:'CACHE', f2:'CACHE', f3:'DONT_CACHE', f4:'DONT_CACHE'}, functions)
        
        
    """
    def test_cache_folder_exists_when_cache_folder_does_not_exist(self):
        self.assertFalse(_cache_folder_exists())

    def test_db_exists_when_db_exists(self):
        os.mkdir(self.FOLDER_NAME)
        with open('.intpy/intpy.db', 'wt'): pass
        self.assertTrue(_db_exists())
    
    def test_db_exists_when_db_does_not_exist(self):
        self.assertFalse(_db_exists())

    def test_folder_exists_when_folder_exists(self):
        os.mkdir(self.FOLDER_NAME)
        self.assertTrue(_folder_exists())
    
    def test_folder_exists_when_folder_does_not_exist(self):
        self.assertFalse(_folder_exists())

    def test_env_exists_when_env_exists(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        with open('.intpy/intpy.db', 'wt'): pass
        self.assertTrue(_env_exists())
    
    def test_env_exists_when_env_partially_not_exist(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        self.assertFalse(_env_exists())

    def test_env_exists_when_env_does_not_exist(self):
        self.assertFalse(_folder_exists())

    def test_create_database(self):
        os.mkdir(self.FOLDER_NAME)
        self.assertFalse(os.path.exists('.intpy/intpy.db'))
        _create_database()
        self.assert_db_exists()

    def test_create_cache_folder(self):
        self.assertFalse(os.path.exists(self.CACHE_FOLDER_NAME))
        _create_cache_folder()
        self.assertTrue(os.path.exists(self.CACHE_FOLDER_NAME))

    def test_create_folder(self):
        self.assertFalse(os.path.exists(self.FOLDER_NAME))
        _create_folder()
        self.assertTrue(os.path.exists(self.FOLDER_NAME))
    
    def test_init_env_when_env_does_not_exist(self):
        init_env()
        self.assertTrue(os.path.exists(self.CACHE_FOLDER_NAME))
        self.assert_db_exists()
    
    def test_init_env_when_env_partially_exists(self):
        os.mkdir(self.FOLDER_NAME)
        init_env()
        self.assertTrue(os.path.exists(self.CACHE_FOLDER_NAME))
        self.assert_db_exists()
    """
if __name__ == '__main__':
    unittest.main()