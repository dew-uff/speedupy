import unittest, mysql.connector, redis, pymongo, os, sys, random, pickle, shutil
from pathlib import Path

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from entities.BancoSQLite import BancoSQLite
from setup_exp.services.environment_service import _create_databases, _create_cache_folder, _create_folder, _cache_folder_exists, _folder_exists, _env_exists, init_env

class TestEnvironmentService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.FOLDER_NAME = ".speedupy"
        cls.CACHE_FOLDER_NAME = os.path.join(cls.FOLDER_NAME, "cache")
        cls.SQLITE_DB_FILENAME = os.path.join(cls.FOLDER_NAME, "speedupy.db")

        try:
            cls.redis = redis.Redis(host='localhost', port=6379, db=0)
            cls.redis.ping()
        except: cls.redis = None

        try:
            cls.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=1000)
            cls.mongo_client.server_info()
            cls.mongo = cls.mongo_client['speedupy']['CACHE']
        except: 
            cls.mongo_client = None
            cls.mongo = None

    def setUp(self):
        if os.path.exists(self.FOLDER_NAME):
            shutil.rmtree(self.FOLDER_NAME)
            
        try:
            self.mysql_client = mysql.connector.connect(host="127.0.0.1", user="root")
            self.mysql = self.mysql_client.cursor()
        except:
            self.mysql_client = None
            self.mysql = None

    @classmethod
    def tearDownClass(cls):
        if cls.redis: cls.redis.close()
        if cls.mongo_client: cls.mongo_client.close()

    def tearDown(self):
        if os.path.exists(self.FOLDER_NAME):
            shutil.rmtree(self.FOLDER_NAME)
            
        if self.redis: 
            try: self.redis.flushdb()
            except: pass
        if self.mongo_client: 
            try: self.mongo_client.drop_database('speedupy')
            except: pass
        if self.mysql_client:
            try: 
                self.mysql.execute('DROP DATABASE IF EXISTS speedupy')
                self.mysql_client.close()
            except: pass

    def populate_redis_database(self):
        if self.redis:
            for i in range(5): self.redis.set(str(i), pickle.dumps(random.random()))

    def populate_mongo_database(self):
        if self.mongo is not None:
            for i in range(5): self.mongo.insert_one({"_id": str(i), "value": pickle.dumps(random.random())})

    def populate_mysql_database(self):
        if self.mysql:
            self.mysql.execute('CREATE DATABASE IF NOT EXISTS speedupy')
            self.mysql.execute('USE speedupy')
            create_cache_table_sql = """
                CREATE TABLE IF NOT EXISTS CACHE (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    func_call_hash TEXT,
                    func_output LONGBLOB,
                    func_name TEXT,
                    UNIQUE (func_call_hash(255))
                ) ENGINE=InnoDB;
            """
            self.mysql.execute(create_cache_table_sql)
            for i in range(5): self.mysql.execute('INSERT INTO CACHE(func_call_hash, func_output) VALUES (%s, %s)', (str(i), pickle.dumps(random.random())))
            self.mysql_client.commit()

    def assert_sqlite_db_exists(self):
        self.assertTrue(os.path.exists(self.SQLITE_DB_FILENAME))
        BancoSQLite.nome_banco = self.SQLITE_DB_FILENAME
        if BancoSQLite.database_exists():
            conexao_banco = BancoSQLite()
            conexao_banco.close_connection()

    def test_create_cache_folder(self):
        _create_folder() 
        self.assertFalse(os.path.exists(self.CACHE_FOLDER_NAME))
        _create_cache_folder()
        self.assertTrue(os.path.exists(self.CACHE_FOLDER_NAME))

    def test_create_folder(self):
        self.assertFalse(os.path.exists(self.FOLDER_NAME))
        _create_folder()
        self.assertTrue(os.path.exists(self.FOLDER_NAME))

    def test_create_database_when_sqlite_database_does_not_exist(self):
        _create_folder()

        if self.redis:
            with self.subTest(storage='redis'):
                self.populate_redis_database()
                self.assertEqual(self.redis.dbsize(), 5)
                _create_databases('redis')
                self.assertEqual(self.redis.dbsize(), 0)

        if self.mongo is not None:
            with self.subTest(storage='mongo'):
                self.populate_mongo_database()
                self.assertEqual(self.mongo.count_documents({}), 5)
                _create_databases('mongo')
                self.assertEqual(self.mongo.count_documents({}), 0)

        if self.mysql:
            with self.subTest(storage='mysql'):
                self.populate_mysql_database()
                self.mysql.execute("SELECT COUNT(*) FROM CACHE")
                self.assertTupleEqual(self.mysql.fetchone(), (5,))
                self.mysql_client.commit()
                _create_databases('mysql') 
                self.mysql.execute("USE speedupy")
                self.mysql.execute("SELECT COUNT(*) FROM CACHE")
                self.assertTupleEqual(self.mysql.fetchone(), (0,))

        with self.subTest(storage='sqlite'):
            self.assertFalse(os.path.exists(self.SQLITE_DB_FILENAME))
            _create_databases('sqlite')
            self.assertTrue(os.path.exists(self.SQLITE_DB_FILENAME))

    def test_create_database_when_sqlite_database_exists(self):
        _create_folder()
        Path(self.SQLITE_DB_FILENAME).touch()

        if self.redis:
            with self.subTest(storage='redis'):
                self.populate_redis_database()
                _create_databases('redis')
                self.assertEqual(self.redis.dbsize(), 0)

        if self.mysql:
            with self.subTest(storage='mysql'):
                self.populate_mysql_database()
                _create_databases('mysql')
                self.mysql.execute("USE speedupy")
                self.mysql.execute("SELECT COUNT(*) FROM CACHE")
                self.assertTupleEqual(self.mysql.fetchone(), (0,))

    def test_init_env_with_sqlite(self):
        init_env('sqlite')
        self.assertTrue(os.path.exists(self.CACHE_FOLDER_NAME))
        self.assertTrue(os.path.exists(self.SQLITE_DB_FILENAME))

    def test_init_env_with_file(self):
        init_env('file')
        self.assertTrue(os.path.exists(self.CACHE_FOLDER_NAME))
        self.assertFalse(os.path.exists(self.SQLITE_DB_FILENAME))

    def test_init_env_with_redis(self):
        if self.redis:
            self.populate_redis_database()
            init_env('redis')
            self.assertEqual(self.redis.dbsize(), 0)
            self.assertFalse(os.path.exists(self.SQLITE_DB_FILENAME))

if __name__ == '__main__':
    unittest.main()