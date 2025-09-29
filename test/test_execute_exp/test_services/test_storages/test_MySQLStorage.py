import unittest
import os
import sys
from typing import Dict
from pickle import dumps, loads

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.storages.MySQLStorage import MySQLStorage
from execute_exp.services.storages.Storage import Storage
from execute_exp.entitites.CacheData import CacheData
from entities.BancoMySQL import BancoMySQL
from test_execute_exp.test_services.test_storages.AbstractStorageTest import AbstractStorageTest

class TestMySQLStorage(AbstractStorageTest, unittest.TestCase):

    def setUp(self):
        """ Roda antes de cada teste """
        self.banco = BancoMySQL()
        if not self.banco.conexao:
            self.fail("A conexão com o MySQL falhou. Os testes não podem continuar.")
        
        self.banco.cursor.execute("DROP TABLE IF EXISTS CACHE;")
        self.banco.create_database()
        
        super().setUp()

    def tearDown(self):
        """ Roda depois de cada teste """
        if hasattr(self, 'banco') and self.banco:
            self.banco.close_connection()
        super().tearDown()

    def create_instance(self) -> Storage:
        """ Cria a instância injetando a conexão do teste. """
        return MySQLStorage(self.banco)

    def assert_storage_is_empty(self):
        """ Verifica se a tabela CACHE no MySQL está vazia. """
        resp = self.banco.select("SELECT COUNT(*) FROM CACHE")
        self.assertEqual(resp[0][0], 0)

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        """ Verifica se os dados no MySQL são exatamente os esperados. """
        sql = 'SELECT func_call_hash, func_output, func_name FROM CACHE'
        resp = self.banco.select(sql)
        data_gotten = {}
        for row in resp:
            fc_hash, fc_output, fc_name = row
            data_gotten[fc_hash] = CacheData(fc_hash, loads(fc_output), func_name=fc_name)
        self.assert_data_gotten_is_correct(data_gotten, expected_data)

    def manually_cache_a_record(self, func_hash, func_return, func_name=None, **kwargs):
        """ Insere um registro de teste diretamente no banco de dados MySQL. """
        if func_name:
            sql_stmt = 'INSERT INTO CACHE(func_call_hash, func_output, func_name) VALUES (%s, %s, %s)'
            sql_params = (func_hash, dumps(func_return), func_name)
        else:
            sql_stmt = 'INSERT INTO CACHE(func_call_hash, func_output) VALUES (%s, %s)'
            sql_params = (func_hash, dumps(func_return))
        
        self.banco.exec_without_output(sql_stmt, sql_params)