import os
import sqlite3
import unittest
from typing import Dict
from unittest.mock import Mock

from remove_paths import remove_paths

from constants import Constants
from entities.SQLiteDatabase import SQLiteDatabase
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.serializers.PickleSerializer import PickleSerializer
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.SQLiteStorage import SQLiteStorage
from execute_exp.services.storages.Storage import Storage
from test_execute_exp.test_services.test_storages.AbstractStorageTest import (
    AbstractStorageTest,
)


class TestSQLiteStorage(AbstractStorageTest, unittest.TestCase):
    def setUp(self):
        self.databases = []
        super().setUp()

    def tearDown(self):
        # Windows refuses to remove a database file that is still open.
        for database in self.databases:
            database.close_connection()
        super().tearDown()

    def create_instance(self, serializer: Serializer) -> Storage:
        self.create_database()
        storage = SQLiteStorage(serializer)
        self.databases.append(storage._SQLiteStorage__local.db_connection)
        # The tests of this class read through the storage's own connection, which
        # sees uncommitted rows; TestSQLiteStorageCommits covers the commit.
        storage._SQLiteStorage__local.db_connection.commit = Mock()
        self.storage_conn = storage._SQLiteStorage__local.db_connection.connection
        return storage

    def create_database(self):
        stmt = "CREATE TABLE IF NOT EXISTS CACHE (\
        id INTEGER PRIMARY KEY AUTOINCREMENT,\
        func_call_hash TEXT UNIQUE,\
        func_output BLOB,\
        func_name TEXT\
        );"
        self.conn = sqlite3.connect(Constants().DB_PATH)
        self.conn.execute(stmt)
        self.conn.commit()
        self.conn.close()

    def assert_storage_is_empty(self):
        resp = self.storage_conn.execute("SELECT * FROM CACHE").fetchall()
        self.assertListEqual(resp, [])

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        sql = "SELECT func_call_hash, func_output, func_name FROM CACHE"
        resp = self.storage_conn.execute(sql).fetchall()
        data_gotten = {}
        for row in resp:
            fc_hash = row[0]
            fc_output = self.serializer.loads(row[1])
            fc_name = row[2]
            data_gotten[fc_hash] = CacheData(fc_hash, fc_output, func_name=fc_name)
        self.assert_data_gotten_is_correct(data_gotten, expected_data)

    def manually_cache_a_record(self, func_hash, func_return, func_name=None, **kwargs):
        sql_stmt = "INSERT INTO CACHE(func_call_hash, func_output) VALUES (?, ?)"
        sql_params = [func_hash, self.serializer.dumps(func_return)]
        if func_name:
            sql_stmt = "INSERT INTO CACHE(func_call_hash, func_output, func_name) VALUES (?, ?, ?)"
            sql_params.append(func_name)
        self.storage_conn.execute(sql_stmt, sql_params)
        if "commit" in kwargs and kwargs["commit"]:
            self.storage_conn.commit()


class TestSQLiteStorageCommits(unittest.TestCase):
    """Issue #86: what save_cache_data writes is committed when it returns.

    The storage is built without the mocked commit of TestSQLiteStorage, and
    the rows are read through a fresh connection to the file while the storage
    is still alive, so nothing can rely on the instance being finalized.
    """

    def setUp(self):
        remove_paths(Constants().FOLDER_NAME)
        os.makedirs(Constants().FOLDER_NAME)
        database = SQLiteDatabase()
        database.create_database()
        database.close_connection()
        self.serializer = PickleSerializer()
        self.storage = SQLiteStorage(self.serializer)

    def tearDown(self):
        self.storage._SQLiteStorage__local.db_connection.close_connection()
        remove_paths(Constants().FOLDER_NAME)

    def read_rows_through_a_fresh_connection(self):
        conn = sqlite3.connect(Constants().DB_PATH)
        try:
            rows = conn.execute(
                "SELECT func_call_hash, func_output, func_name FROM CACHE"
            ).fetchall()
        finally:
            conn.close()
        return {h: (self.serializer.loads(out), name) for h, out, name in rows}

    def test_save_cache_data_is_visible_to_a_fresh_connection(self):
        self.storage.save_cache_data(
            {"hash1": CacheData("hash1", 10), "hash2": CacheData("hash2", [1, 2])}
        )
        self.assertDictEqual(
            self.read_rows_through_a_fresh_connection(),
            {"hash1": (10, None), "hash2": ([1, 2], None)},
        )

    def test_save_cache_data_with_func_name_is_visible_to_a_fresh_connection(self):
        self.storage.save_cache_data(
            {"hash1": CacheData("hash1", "out", func_name="f")}
        )
        self.assertDictEqual(
            self.read_rows_through_a_fresh_connection(), {"hash1": ("out", "f")}
        )
