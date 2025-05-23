import sqlite3, unittest, os, sys
from unittest.mock import Mock
from typing import Dict
from pickle import dumps, loads

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.storages.SQLiteStorage import SQLiteStorage
from execute_exp.services.storages.Storage import Storage
from execute_exp.entitites.CacheData import CacheData
from constantes import Constantes
from test_execute_exp.test_services.test_storages.AbstractStorageTest import AbstractStorageTest


# XXX: CONTINUAR REFATORAÇÃO
class TestSQLiteStorage(AbstractStorageTest, unittest.TestCase):
    @classmethod
    def create_database(cls):
        stmt = "CREATE TABLE IF NOT EXISTS CACHE (\
        id INTEGER PRIMARY KEY AUTOINCREMENT,\
        func_call_hash TEXT UNIQUE,\
        func_output BLOB,\
        func_name TEXT\
        );"
        cls.conn = sqlite3.connect(Constantes().BD_PATH)
        cls.conn.execute(stmt)
        cls.conn.commit()
        cls.conn.close()

    def create_instance(self) -> Storage:
        self.create_database()
        storage = SQLiteStorage()
        storage._SQLiteStorage__local.db_connection.salvar_alteracoes = Mock() # Preventing DB connection to commit changes when SQLiteStorage instance is destroyed
        self.storage_conn = storage._SQLiteStorage__local.db_connection.conexao
        return storage

    def assert_storage_is_empty(self):
        resp = self.storage_conn.execute("SELECT * FROM CACHE").fetchall()
        self.assertListEqual(resp, [])

    def assert_cache_data_correctly_inserted(self, expected_data: Dict[str, CacheData]):
        sql = 'SELECT func_call_hash, func_output, func_name FROM CACHE'
        resp = self.storage_conn.execute(sql).fetchall()
        data_gotten = {}
        for row in resp:
            fc_hash = row[0]
            fc_output = loads(row[1])
            fc_name = row[2]
            data_gotten[fc_hash] = CacheData(fc_hash, fc_output, func_name=fc_name)
        self.assert_data_gotten_is_correct(data_gotten, expected_data)

    def assert_data_gotten_is_correct(self, data_gotten: Dict[str, CacheData], expected_data: Dict[str, CacheData]):
        self.assertListEqual(list(data_gotten.keys()), list(expected_data.keys()))
        for func_call_hash in data_gotten:
            self.assert_two_cache_data_are_equal(data_gotten[func_call_hash],
                                                 expected_data[func_call_hash])

    def assert_two_cache_data_are_equal(self, cache_data_1: CacheData, cache_data_2: CacheData):
        self.assertEqual(cache_data_1.function_call_hash, cache_data_2.function_call_hash)
        self.assertEqual(cache_data_1.func_name, cache_data_2.func_name)
        self.assertEqual(dumps(cache_data_1.output), dumps(cache_data_2.output))

    def manually_cache_a_record(self, func_hash, func_return, func_name=None, commit=False):
        sql_stmt = 'INSERT INTO CACHE(func_call_hash, func_output) VALUES (?, ?)'
        sql_params = [func_hash, dumps(func_return)]
        if func_name:
            sql_stmt = 'INSERT INTO CACHE(func_call_hash, func_output, func_name) VALUES (?, ?, ?)'
            sql_params.append(func_name)
        self.storage_conn.execute(sql_stmt, sql_params)
        if commit: self.storage_conn.commit()
