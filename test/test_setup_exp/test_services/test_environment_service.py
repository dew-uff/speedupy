import os
import pickle
import random
import unittest
from pathlib import Path

import gridfs
import mysql.connector
import pymongo
import redis
from pymemcache.client.base import Client
from pymemcache.serde import pickle_serde
from remove_paths import remove_paths

from entities.SQLiteDatabase import SQLiteDatabase
from execute_exp.parser_params import STORAGE_OPTIONS
from setup_exp.services.environment_service import _create_databases


class TestEnvironmentService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.FOLDER_NAME = ".speedupy"
        cls.CACHE_FOLDER_NAME = os.path.join(cls.FOLDER_NAME, "cache")
        cls.SQLITE_DB_FILENAME = os.path.join(cls.FOLDER_NAME, "speedupy.db")

        cls.redis = redis.Redis(host="localhost", port=6379, db=0)
        cls.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        cls.mongo = cls.mongo_client["speedupy"]["CACHE"]
        cls.gridfs = cls.mongo_client["speedupy"]["CACHE_GRIDFS"]
        cls.gridfs_bucket = gridfs.GridFSBucket(
            cls.mongo_client["speedupy"], bucket_name="CACHE_GRIDFS"
        )
        cls.memcached = Client(
            ("localhost", 11211),
            serializer=pickle_serde.serialize,
            deserializer=pickle_serde.deserialize,
        )

    def setUp(self):
        # The tests count what they put in the servers: start them empty,
        # whatever the tests that ran before left there.
        self.clear_servers()
        self.mysql_client = mysql.connector.connect(host="127.0.0.1", user="root")
        self.mysql = self.mysql_client.cursor()

    @classmethod
    def tearDownClass(cls):
        cls.redis.close()
        cls.mongo_client.close()
        cls.memcached.close()

    def tearDown(self):
        # A test may close self.mysql midway; a failure before it reconnects
        # must not turn into a teardown error that hides it.
        self.mysql.close()
        self.mysql_client.close()
        self.clear_servers()

    def clear_servers(self):
        remove_paths(self.FOLDER_NAME)
        self.redis.flushdb()
        self.mongo_client.drop_database("speedupy")
        self.memcached.flush_all(noreply=False)
        mysql_client = mysql.connector.connect(host="127.0.0.1", user="root")
        mysql_client.cursor().execute("DROP DATABASE IF EXISTS speedupy")
        mysql_client.close()

    def count_memcached_items(self):
        # flush_all hides the items at once but curr_items drops only later,
        # when they are read or crawled: count the keys populate_memcached_cache
        # writes instead.
        return len(self.memcached.get_many([str(i) for i in range(5)]))

    def populate_redis_database(self):
        for i in range(5):
            self.redis.set(str(i), pickle.dumps(random.random()))

    def populate_mongo_database(self):
        for i in range(5):
            self.mongo.insert_one(
                {"_id": str(i), "value": pickle.dumps(random.random())}
            )

    def populate_gridfs_database(self):
        for i in range(5):
            self.gridfs_bucket.upload_from_stream(str(i), pickle.dumps(random.random()))

    def populate_memcached_cache(self):
        for i in range(5):
            self.memcached.set(str(i), random.random())

    def populate_mysql_database(self):
        self.mysql.execute("CREATE DATABASE IF NOT EXISTS speedupy")
        self.mysql.execute("USE speedupy")
        create_cache_table_sql = """
            CREATE TABLE IF NOT EXISTS CACHE (
                id INT PRIMARY KEY AUTO_INCREMENT,
                func_call_hash TEXT,
                func_output BLOB,
                func_name TEXT,
                UNIQUE (func_call_hash(255))
            ) ENGINE=InnoDB;
        """
        self.mysql.execute(create_cache_table_sql)
        for i in range(5):
            self.mysql.execute(
                "INSERT INTO CACHE(func_call_hash, func_output) VALUES (%s, %s)",
                (str(i), pickle.dumps(random.random())),
            )
        self.mysql_client.commit()

    def assert_sqlite_db_exists(self):
        self.assertTrue(os.path.exists(self.SQLITE_DB_FILENAME))
        expeceted_result = {("sqlite_sequence",), ("CACHE",), ("FUNCTION_CALLS_PROV",)}
        SQLiteDatabase.db_path = self.SQLITE_DB_FILENAME
        conexao_banco = SQLiteDatabase()
        resp = conexao_banco.select(
            "SELECT tbl_name FROM sqlite_master WHERE type = 'table'"
        )
        self.assertSetEqual(set(resp), expeceted_result)

    def populate_all_servers(self):
        self.populate_redis_database()
        self.populate_mongo_database()
        self.populate_gridfs_database()
        self.populate_memcached_cache()
        self.populate_mysql_database()

    def assert_only_emptied(self, storage, emptied):
        """Fill every server, set up ``storage``, check what it emptied.

        ``emptied`` names the servers the storage owns. Each of them must end
        empty and every other one must still hold its 5 items: setup never
        touches a server that was not selected.
        """
        os.mkdir(self.FOLDER_NAME)
        self.populate_all_servers()
        self.assertFalse(os.path.exists(self.SQLITE_DB_FILENAME))
        # The MySQL setup drops and recreates its database: release it first.
        self.mysql.close()
        self.mysql_client.close()

        _create_databases(storage)

        self.assert_sqlite_db_exists()
        self.mysql_client = mysql.connector.connect(
            host="127.0.0.1", user="root", database="speedupy"
        )
        self.mysql = self.mysql_client.cursor()
        self.mysql.execute("SELECT COUNT(*) FROM CACHE")
        held = {
            "redis": self.redis.dbsize(),
            "mongo": self.mongo.count_documents({}),
            "gridfs": self.gridfs.files.count_documents({}),
            "memcached": self.count_memcached_items(),
            "mysql": self.mysql.fetchone()[0],
        }
        expected = {
            server: 0 if server in emptied else 5
            for server in ("redis", "mongo", "gridfs", "memcached", "mysql")
        }
        self.assertDictEqual(held, expected)

    def test_create_databases_for_redis_empties_only_redis(self):
        self.assert_only_emptied("redis", {"redis"})

    # The four Mongo-backed storages share one MongoDB database (`speedupy`),
    # so setting up any of them empties the collections of all of them.
    MONGODB = {"mongo", "gridfs"}

    def test_create_databases_for_mongo_empties_only_mongodb(self):
        self.assert_only_emptied("mongo", self.MONGODB)

    def test_create_databases_for_mongo_file_empties_only_mongodb(self):
        self.assert_only_emptied("mongo-file", self.MONGODB)

    def test_create_databases_for_gridfs_empties_only_mongodb(self):
        self.assert_only_emptied("gridfs", self.MONGODB)

    def test_create_databases_for_mongo_gridfs_empties_only_mongodb(self):
        self.assert_only_emptied("mongo-gridfs", self.MONGODB)

    def test_create_databases_for_mysql_empties_only_mysql(self):
        self.assert_only_emptied("mysql", {"mysql"})

    def test_create_database_when_sqlite_database_exists(self):
        os.mkdir(self.FOLDER_NAME)
        Path(self.SQLITE_DB_FILENAME).touch()
        self.populate_all_servers()

        for storage in STORAGE_OPTIONS:
            with self.subTest(storage=storage):
                _create_databases(storage)

        self.assertEqual(self.redis.dbsize(), 5)
        self.assertEqual(self.mongo.count_documents({}), 5)
        self.assertEqual(self.gridfs.files.count_documents({}), 5)
        self.assertEqual(self.count_memcached_items(), 5)
        self.mysql.execute("SELECT COUNT(*) FROM CACHE")
        self.assertTupleEqual(self.mysql.fetchone(), (5,))


if __name__ == "__main__":
    unittest.main()
