import unittest, os, sys
from unittest.mock import Mock
from typing import Dict

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.storages.DBStorage import DBStorage
from constantes import Constantes
from pickle import dumps
import sqlite3

class TestDBStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Constantes().FOLDER_NAME = '.speedupy_test/'
        Constantes().BD_PATH = '.speedupy_test/speedupy.db'
        cls.create_database()

    @classmethod
    def create_database(cls):
        stmt = "CREATE TABLE IF NOT EXISTS CACHE (\
        id INTEGER PRIMARY KEY AUTOINCREMENT,\
        func_call_hash TEXT UNIQUE,\
        func_output BLOB,\
        func_name TEXT\
        );"
        os.mkdir(Constantes().FOLDER_NAME)
        cls.conn = sqlite3.connect(Constantes().BD_PATH)
        cls.conn.execute(stmt)
        cls.conn.commit()
        cls.conn.close()

    @classmethod
    def tearDownClass(cls):
        os.system(f'rm -rf {Constantes().FOLDER_NAME}/')
    
    def setUp(self):
        self.storage = DBStorage()
        self.storage_conn = self.storage._DBStorage__db_connection.conexao
        self.storage._DBStorage__db_connection.salvarAlteracoes = Mock() #Preventing DB connection to commit changes when DBStorage instance is destroyed
        self.assert_db_is_empty()

    def assert_db_is_empty(self):
        resp = self.storage_conn.execute("SELECT * FROM CACHE").fetchall()
        self.assertListEqual(resp, [])
    
    def assert_cache_data_correctly_inserted(self, expected_data:Dict):
        #expected_data = {func_call_hash (str): {'func_name': (Optional[str]),
        #                                        'output': (Any)}
        #                }
        sql = 'SELECT func_call_hash, func_output, func_name FROM CACHE'
        resp = self.storage_conn.execute(sql).fetchall()
        self.assertEqual(len(resp), len(expected_data))
        for row in resp:
            fc_hash = row[0]
            fc_output = row[1]
            fc_name = row[2]
            self.assertIn(fc_hash, expected_data)
            self.assertEqual(fc_output, dumps(expected_data[fc_hash]['output']))
            self.assertEqual(fc_name, expected_data[fc_hash]['func_name'])
    
    def manually_cache_a_record(self, func_hash, func_return, func_name=None, commit=False):
        sql_stmt = 'INSERT INTO CACHE(func_call_hash, func_output) VALUES (?, ?)'
        sql_params = [func_hash, dumps(func_return)]
        if func_name:
            sql_stmt = 'INSERT INTO CACHE(func_call_hash, func_output, func_name) VALUES (?, ?, ?)'
            sql_params.append(func_name)
        self.storage_conn.execute(sql_stmt, sql_params)
        if commit: self.storage_conn.commit()

    def clean_database(self):
        self.storage_conn.execute('DELETE FROM CACHE WHERE id > 0')
        self.storage_conn.commit()

    def test_get_all_cached_data_when_there_is_no_cache_record(self):
        dicio = self.storage.get_all_cached_data()
        self.assertDictEqual(dicio, {})

    def test_get_all_cached_data_when_there_is_one_cache_record(self):
        self.manually_cache_a_record('func_call_hash', (1, True, MyClass()))
        dicio = self.storage.get_all_cached_data()
        self.assertListEqual(list(dicio.keys()), ['func_call_hash'])
        self.assertEqual(dumps(dicio['func_call_hash']), dumps((1, True, MyClass())))
        
    def test_get_all_cached_data_when_there_are_many_cache_records(self):
        self.manually_cache_a_record('func_call_hash1', 1.12312)
        self.manually_cache_a_record('func_call_hash2', False)
        self.manually_cache_a_record('func_call_hash3', 'My test')
        self.manually_cache_a_record('func_call_hash4', {-1, True, 10})
        
        dicio = self.storage.get_all_cached_data()
        self.assertDictEqual(dicio, {'func_call_hash1': 1.12312,
                                     'func_call_hash2': False,
                                     'func_call_hash3': 'My test',
                                     'func_call_hash4': {-1, True, 10}})

    def test_get_all_cached_data_using_an_isolated_connection(self):
        self.manually_cache_a_record('func_call_hash1', -123.3, commit=True)
        self.manually_cache_a_record('func_call_hash2', True, commit=True)
        
        dicio = self.storage.get_all_cached_data(use_isolated_connection=True)
        self.assertDictEqual(dicio, {'func_call_hash1': -123.3,
                                     'func_call_hash2': True})
        
        self.clean_database()

    def test_get_cached_data_of_a_function_when_there_is_no_record(self):
        dicio = self.storage.get_cached_data_of_a_function('f1')
        self.assertDictEqual(dicio, {})

    def test_get_cached_data_of_a_function_when_there_is_no_record_for_the_requested_function_but_for_other_functions_there_are_records(self):
        self.manually_cache_a_record('func_call_hash1', 1.12312, func_name='f2')
        self.manually_cache_a_record('func_call_hash2', False, func_name='f2')
        self.manually_cache_a_record('func_call_hash3', 'My test', func_name='f3')
        
        dicio = self.storage.get_cached_data_of_a_function('f1')
        self.assertDictEqual(dicio, {})

    def test_get_cached_data_of_a_function_when_there_is_one_record(self):
        self.manually_cache_a_record('func_call_hash1', 1.12312, func_name='f1')
        self.manually_cache_a_record('func_call_hash2', True, func_name='f2')
        self.manually_cache_a_record('func_call_hash3', {1, 4, -2}, func_name='f2')
        
        dicio = self.storage.get_cached_data_of_a_function('f1')
        self.assertDictEqual(dicio, {'func_call_hash1':1.12312})

    def test_get_cached_data_of_a_function_when_there_are_many_record(self):
        self.manually_cache_a_record('func_call_hash1', 1.12312, func_name='f1')
        self.manually_cache_a_record('func_call_hash2', True, func_name='f1')
        self.manually_cache_a_record('func_call_hash3', {1, 4, -2}, func_name='f1')
        self.manually_cache_a_record('func_call_hash4', 'my test', func_name='f2')
        
        dicio = self.storage.get_cached_data_of_a_function('f1')
        self.assertDictEqual(dicio, {'func_call_hash1':1.12312,
                                     'func_call_hash2':True,
                                     'func_call_hash3':{1, 4, -2}})

    def test_get_cached_data_of_a_function_using_an_isolated_connection(self):
        self.manually_cache_a_record('func_call_hash1', 'My Test', func_name='f1', commit=True)
        self.manually_cache_a_record('func_call_hash2', {1, 4, -2}, func_name='f1', commit=True)
        self.manually_cache_a_record('func_call_hash3', 10, func_name='f2', commit=True)
        self.manually_cache_a_record('func_call_hash4', {1, 5, 4}, func_name='f2', commit=True)
        
        dicio = self.storage.get_cached_data_of_a_function('f1', use_isolated_connection=True)
        self.assertDictEqual(dicio, {'func_call_hash1':'My Test',
                                     'func_call_hash2':{1, 4, -2}})
        
        self.clean_database()

    def test_get_cached_data_of_a_function_call_when_cache_record_doesnt_exist(self):
        value = self.storage.get_cached_data_of_a_function_call('func_call_hash')
        self.assertIsNone(value)

    def test_get_cached_data_of_a_function_call_when_cache_record_doesnt_exist_but_other_records_exist(self):
        self.manually_cache_a_record('func_call_hash1', 'My Test')
        self.manually_cache_a_record('func_call_hash2', {1, 4, -2})
        self.manually_cache_a_record('func_call_hash3', 10)

        value = self.storage.get_cached_data_of_a_function_call('func_call_hash0')
        self.assertIsNone(value)

    def test_get_cached_data_of_a_function_call_when_cache_record_exists(self):
        self.manually_cache_a_record('func_call_hash1', 3.1415)
        self.manually_cache_a_record('func_call_hash2', [1, {2, 4, 1}, -2])
        self.manually_cache_a_record('func_call_hash3', 'My test')

        value = self.storage.get_cached_data_of_a_function_call('func_call_hash1')
        self.assertEqual(value, 3.1415)

    def test_get_cached_data_of_a_function_call_using_an_isolated_connection(self):
        self.manually_cache_a_record('func_call_hash1', -3.1415, commit=True)
        self.manually_cache_a_record('func_call_hash2', [1, {2, 4, 1}, -2], commit=True)
        self.manually_cache_a_record('func_call_hash3', 'My test', commit=True)

        value = self.storage.get_cached_data_of_a_function_call('func_call_hash1',
                                                                use_isolated_connection=True)
        self.assertEqual(value, -3.1415)
        self.clean_database()
 
    def test_save_cache_data_when_there_is_no_data_to_save(self):
        self.storage.save_cache_data({})
        self.assert_cache_data_correctly_inserted({})

    def test_save_cache_data_when_there_is_one_record_to_save_without_func_name(self):
        data = {'func_call_hash':{'func_name':None, 'output':{1, 5, 4}}}
        self.storage.save_cache_data(data)
        self.assert_cache_data_correctly_inserted(data)

    def test_save_cache_data_when_there_is_one_record_to_save_with_func_name(self):
        data = {'func_call_hash':{'func_name':'f1', 'output':{1, True}}}
        self.storage.save_cache_data(data)
        self.assert_cache_data_correctly_inserted(data)

    def test_save_cache_data_when_there_are_many_records_to_save_without_func_name(self):
        data = {'func_call_hash1':{'func_name':None, 'output':{1, True}},
                'func_call_hash2':{'func_name':None, 'output':('test',)},
                'func_call_hash3':{'func_name':None, 'output':-23.123}}
        self.storage.save_cache_data(data)
        self.assert_cache_data_correctly_inserted(data)

    def test_save_cache_data_when_there_are_many_records_to_save_with_func_name(self):
        data = {'func_call_hash1':{'func_name':'f1', 'output':{1, True}},
                'func_call_hash2':{'func_name':'f2', 'output':('test',)},
                'func_call_hash3':{'func_name':'f2', 'output':-23.123},
                'func_call_hash4':{'func_name':'f3', 'output':MyClass()}}
        self.storage.save_cache_data(data)
        self.assert_cache_data_correctly_inserted(data)

    def test_save_cache_data_using_an_isolated_connection(self):
        data = {'func_call_hash1':{'func_name':'f1', 'output':{1, True}},
                'func_call_hash2':{'func_name':'f2', 'output':-23.123},
                'func_call_hash3':{'func_name':'f3', 'output':MyClass()}}
        self.storage.save_cache_data(data, use_isolated_connection=True)
        self.assert_cache_data_correctly_inserted(data)
        
        self.clean_database()

class MyClass():
    def __init__(self):
        self.__x = 10
        self.__y = 20