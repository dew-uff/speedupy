import unittest, unittest.mock, os, sys, random
from pathlib import Path

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from entities.BancoSQLite import BancoSQLite
from entities.BancoRedis import BancoRedis
from setup_exp.services.environment_service import _create_databases, _create_cache_folder, _create_folder, _cache_folder_exists, _folder_exists, _env_exists, init_env


class TestEnvironmentService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.FOLDER_NAME = ".speedupy"
        cls.CACHE_FOLDER_NAME = os.path.join(cls.FOLDER_NAME, "cache")
        cls.SQLITE_DB_FILENAME = os.path.join(cls.FOLDER_NAME, "speedupy.db")

        cls.redis = BancoRedis()

    def tearDown(self):
        os.system("rm -rf {}".format(self.FOLDER_NAME))
        self.redis.flush_database()

    def populate_redis_database(self):
        for i in range(5): self.redis.set(i, random.random())

    def assert_sqlite_db_exists(self):
        self.assertTrue(os.path.exists(self.SQLITE_DB_FILENAME))
        expeceted_result = {('sqlite_sequence',), ('CACHE',), ('FUNCTION_CALLS_PROV',)}
        BancoSQLite.nome_banco = self.SQLITE_DB_FILENAME
        conexao_banco = BancoSQLite()
        resp = conexao_banco.executar_comando_sql_select("SELECT tbl_name FROM sqlite_master WHERE type = 'table'")
        self.assertSetEqual(set(resp), expeceted_result)

    def test_cache_folder_exists_when_cache_folder_exists(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        self.assertTrue(_cache_folder_exists())

    def test_cache_folder_exists_when_cache_folder_does_not_exist(self):
        self.assertFalse(_cache_folder_exists())

    def test_db_exists_when_db_exists(self):
        os.mkdir(self.FOLDER_NAME)
        Path(self.SQLITE_DB_FILENAME).touch()
        self.assertTrue(BancoSQLite.database_exists())

    def test_db_exists_when_db_does_not_exist(self):
        self.assertFalse(BancoSQLite.database_exists())

    def test_folder_exists_when_folder_exists(self):
        os.mkdir(self.FOLDER_NAME)
        self.assertTrue(_folder_exists())

    def test_folder_exists_when_folder_does_not_exist(self):
        self.assertFalse(_folder_exists())

    def test_env_exists_when_env_exists(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        Path(self.SQLITE_DB_FILENAME).touch()
        self.assertTrue(_env_exists())

    def test_env_exists_when_env_partially_not_exist(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        self.assertFalse(_env_exists())

    def test_env_exists_when_env_does_not_exist(self):
        self.assertFalse(_folder_exists())

    def test_create_database_when_sqlite_database_does_not_exist(self):
        os.mkdir(self.FOLDER_NAME)
        self.populate_redis_database()

        self.assertFalse(os.path.exists(self.SQLITE_DB_FILENAME))
        self.assertEqual(self.redis.dbsize(), 5)

        _create_databases()

        self.assert_sqlite_db_exists()
        self.assertEqual(self.redis.dbsize(), 0)

    def test_create_database_when_sqlite_database_exists(self):
        os.mkdir(self.FOLDER_NAME)
        Path(self.SQLITE_DB_FILENAME).touch()
        self.populate_redis_database()

        _create_databases()

        self.assertEqual(self.redis.dbsize(), 5)

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
        self.assert_sqlite_db_exists()

    def test_init_env_when_env_partially_exists(self):
        os.mkdir(self.FOLDER_NAME)
        init_env()
        self.assertTrue(os.path.exists(self.CACHE_FOLDER_NAME))
        self.assert_sqlite_db_exists()


if __name__ == '__main__':
    unittest.main()