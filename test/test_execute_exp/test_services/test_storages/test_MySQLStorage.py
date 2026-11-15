import unittest
from typing import Dict

from entities.BancoMySQL import BancoMySQL
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.MySQLStorage import MySQLStorage
from execute_exp.services.storages.Storage import Storage
from test_execute_exp.test_services.test_storages.AbstractStorageTest import (
    AbstractStorageTest,
)


class TestMySQLStorage(AbstractStorageTest, unittest.TestCase):
    def setUp(self):
        self.banco = BancoMySQL()
        self.banco.create_database()
        super().setUp()

    def tearDown(self):
        self.banco.close_connection()
        super().tearDown()

    def create_instance(self, serializer: Serializer) -> Storage:
        mysql = MySQLStorage(serializer)
        mysql.db_connection = self.banco
        return mysql

    def assert_storage_is_empty(self):
        resp = self.banco.select("SELECT COUNT(*) FROM CACHE")
        self.assertEqual(resp[0][0], 0)

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        sql = "SELECT func_call_hash, func_output, func_name FROM CACHE"
        resp = self.banco.select(sql)
        data_gotten = {}
        for row in resp:
            fc_hash, fc_output, fc_name = row
            data_gotten[fc_hash] = CacheData(
                fc_hash, self.serializer.loads(fc_output), func_name=fc_name
            )
        self.assert_data_gotten_is_correct(data_gotten, expected_data)

    def manually_cache_a_record(self, func_hash, func_return, func_name=None, **kwargs):
        """Insere um registro de teste diretamente no banco de dados MySQL."""
        if func_name:
            sql_stmt = "INSERT INTO CACHE(func_call_hash, func_output, func_name) VALUES (%s, %s, %s)"
            sql_params = (func_hash, self.serializer.dumps(func_return), func_name)
        else:
            sql_stmt = "INSERT INTO CACHE(func_call_hash, func_output) VALUES (%s, %s)"
            sql_params = (func_hash, self.serializer.dumps(func_return))

        self.banco.cursor.execute(sql_stmt, sql_params)
