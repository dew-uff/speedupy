import unittest, unittest.mock, os, sys

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

import os
from banco import Banco
from setup_exp.environment import _create_database, _create_cache_folder, _create_folder, _cache_folder_exists, _db_exists, _folder_exists, _env_exists, init_env

class TestEnvironment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.FOLDER_NAME = ".speedupy"
        cls.CACHE_FOLDER_NAME = cls.FOLDER_NAME + "/cache"

    def tearDown(self):
        os.system("rm -rf .speedupy/")
    
    def assert_db_exists(self):
        self.assertTrue(os.path.exists('.speedupy/speedupy.db'))
        expeceted_result = {('sqlite_sequence',), ('CACHE',), ('FUNCTION_CALLS_PROV',)}
        conexaoBanco = Banco('.speedupy/speedupy.db')
        resp = conexaoBanco.executarComandoSQLSelect("SELECT tbl_name FROM sqlite_master WHERE type = 'table'")
        self.assertSetEqual(set(resp), expeceted_result)

    def test_cache_folder_exists_when_cache_folder_exists(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        self.assertTrue(_cache_folder_exists())
    
    def test_cache_folder_exists_when_cache_folder_does_not_exist(self):
        self.assertFalse(_cache_folder_exists())

    def test_db_exists_when_db_exists(self):
        os.mkdir(self.FOLDER_NAME)
        with open('.speedupy/speedupy.db', 'wt'): pass
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
        with open('.speedupy/speedupy.db', 'wt'): pass
        self.assertTrue(_env_exists())
    
    def test_env_exists_when_env_partially_not_exist(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        self.assertFalse(_env_exists())

    def test_env_exists_when_env_does_not_exist(self):
        self.assertFalse(_folder_exists())

    def test_create_database(self):
        os.mkdir(self.FOLDER_NAME)
        self.assertFalse(os.path.exists('.speedupy/speedupy.db'))
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

if __name__ == '__main__':
    unittest.main()