import os
import sqlite3
import sys
import unittest
from typing import Dict
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split("test/")[0]
sys.path.append(project_folder)

from constantes import Constantes
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.SQLiteStorage import SQLiteStorage
from execute_exp.services.storages.Storage import Storage
from test_execute_exp.test_services.test_storages.AbstractStorageTest import (
    AbstractStorageTest,
)


class TestSQLiteStorage(AbstractStorageTest, unittest.TestCase):
    def create_instance(self, serializer: Serializer) -> Storage:
        self.create_database()
        storage = SQLiteStorage(serializer)
        storage._SQLiteStorage__local.db_connection.commit = Mock()  # Preventing DB connection to commit changes when SQLiteStorage instance is destroyed
        self.storage_conn = storage._SQLiteStorage__local.db_connection.conexao
        return storage

    def create_database(self):
        stmt = "CREATE TABLE IF NOT EXISTS CACHE (\
        id INTEGER PRIMARY KEY AUTOINCREMENT,\
        func_call_hash TEXT UNIQUE,\
        func_output BLOB,\
        func_name TEXT\
        );"
        self.conn = sqlite3.connect(Constantes().BD_PATH)
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
