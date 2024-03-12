import unittest, os, sys
from unittest.mock import Mock

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

    # def manually_cache_a_record_group_by_function_name(self, func_name, func_hash, func_return):
    #     folder_path = os.path.join(Constantes().CACHE_FOLDER_NAME, func_name)
    #     os.makedirs(folder_path, exist_ok=True)

    #     file_path = os.path.join(func_name, func_hash)
    #     self.manually_cache_a_record(file_path, func_return)
    
    def manually_cache_a_record(self, func_hash, func_return, commit=False):
        self.storage_conn.execute('INSERT INTO CACHE(func_call_hash, func_output) VALUES (?, ?)',
                                  [func_hash, dumps(func_return)])
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

    def test_get_cached_data_of_a_function_when_there_is_no_record(self): pass
    def test_get_cached_data_of_a_function_when_there_is_no_record_for_the_requested_function_but_for_other_functions_there_are_records(self): pass
    def test_get_cached_data_of_a_function_when_there_is_one_record(self): pass
    def test_get_cached_data_of_a_function_when_there_are_many_record(self): pass
    def test_get_cached_data_of_a_function_using_an_isolated_connection(self): pass
        # results = self.__db_connection.executarComandoSQLSelect("SELECT func_call_hash, func_output FROM CACHE WHERE func_name = ?", (func_name,))
        # data = {func_call_hash:pickle.loads(func_output) for func_call_hash, func_output in results}
        # return data





    # def assert_cache_data_correctly_inserted(self, func_call_hash, func_return, func_name=None):
    #     file_path = Constantes().CACHE_FOLDER_NAME
    #     if func_name:
    #         file_path = os.path.join(file_path, func_name, func_call_hash)
    #     else:
    #         file_path = os.path.join(file_path, func_call_hash)
    #     self.assertTrue(os.path.exists(file_path))
    #     with open(file_path, 'rb') as f:
    #         self.assertEqual(f.read(), dumps(func_return))







    
    # def test_get_cached_data_of_a_function_when_there_is_no_cached_data(self):
    #     dicio = self.storage.get_cached_data_of_a_function('f1')
    #     self.assertDictEqual(dicio, {})

    # def test_get_cached_data_of_a_function_when_there_is_cached_data_only_for_other_functions(self):
    #     self.manually_cache_a_record_group_by_function_name('f2', 'func_call_hash1', (True, 2, 5))
    #     self.manually_cache_a_record_group_by_function_name('f2', 'func_call_hash2', [{'key1': 10,
    #                                                                               'key_2': False}])
    #     self.manually_cache_a_record_group_by_function_name('f3', 'func_call_hash3', -123.213)
        
    #     dicio = self.storage.get_cached_data_of_a_function('f1')
    #     self.assertDictEqual(dicio, {})

    # def test_get_cached_data_of_a_function_when_there_is_cached_data_for_it_and_for_other_functions_too(self):
    #     self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash1', 5000.00)
    #     self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash11', (True, 2, 5))
    #     self.manually_cache_a_record_group_by_function_name('f2', 'func_call_hash2', [{'key1': 10,
    #                                                                               'key_2': False}])
    #     self.manually_cache_a_record_group_by_function_name('f3', 'func_call_hash3', -123.213)
        
    #     dicio = self.storage.get_cached_data_of_a_function('f1')
    #     self.assertDictEqual(dicio, {'func_call_hash1': 5000.00,
    #                                  'func_call_hash11': (True, 2, 5)})

    # def test_get_cached_data_of_a_function_when_there_is_a_cached_data_record_for_it(self):
    #     self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash1', {5, 'test', -2.8})
        
    #     dicio = self.storage.get_cached_data_of_a_function('f1')
    #     self.assertDictEqual(dicio, {'func_call_hash1': {5, 'test', -2.8}})
        
    # def test_get_cached_data_of_a_function_when_there_are_many_cached_data_records_for_it(self):
    #     self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash1', 'testing')
    #     self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash2', (1,))
    #     self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash3', [10, -4, False])
    #     self.manually_cache_a_record_group_by_function_name('f3', 'func_call_hash4', -123.213)
        
    #     dicio = self.storage.get_cached_data_of_a_function('f1')
    #     self.assertDictEqual(dicio, {'func_call_hash1': 'testing',
    #                                  'func_call_hash2': (1,),
    #                                  'func_call_hash3': [10, -4, False]})
    
    # def test_get_cached_data_of_a_function_call_when_this_record_doesnt_exist(self):
    #     func_return = self.storage.get_cached_data_of_a_function_call('func_call_hash')
    #     self.assertIsNone(func_return)

    # def test_get_cached_data_of_a_function_call_when_this_record_exists(self):
    #     self.manually_cache_a_record('func_call_hash', (True, 2, 5))

    #     func_return = self.storage.get_cached_data_of_a_function_call('func_call_hash')
    #     self.assertEqual(func_return, (True, 2, 5))

    # def test_get_cached_data_of_a_function_call_when_this_record_doesnt_exist_and_records_are_grouped_by_function_name(self):
    #     func_return = self.storage.get_cached_data_of_a_function_call('func_call_hash', func_name='f1')
    #     self.assertIsNone(func_return)

    # def test_get_cached_data_of_a_function_call_when_this_record_exists_and_records_are_grouped_by_function_name(self):
    #     self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash', 'my_string')

    #     func_return = self.storage.get_cached_data_of_a_function_call('func_call_hash', func_name='f1')
    #     self.assertEqual(func_return, 'my_string')

    # def test_get_cached_data_of_a_function_call_when_this_record_doesnt_exists_but_other_records_exist(self):
    #     self.manually_cache_a_record('func_call_hash1', (True, 2, 5))
    #     self.manually_cache_a_record('func_call_hash2', -12.2131)
    #     self.manually_cache_a_record('func_call_hash3', False)

    #     func_return = self.storage.get_cached_data_of_a_function_call('func_call_hash')
    #     self.assertIsNone(func_return)
    
    # def test_save_cache_data_of_a_function_call_when_function_call_record_doesnt_exist(self):
    #     file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, 'func_call_hash')
    #     self.assertFalse(os.path.exists(file_path))

    #     self.storage._save_cache_data_of_a_function_call('func_call_hash', False)
    #     self.assert_cache_data_correctly_inserted('func_call_hash', False)

    # def test_save_cache_data_of_a_function_call_when_function_call_record_already_exists(self):
    #     self.manually_cache_a_record('func_call_hash', (True, 2, 5))

    #     self.storage._save_cache_data_of_a_function_call('func_call_hash', (True, 2, 5))
    #     self.assert_cache_data_correctly_inserted('func_call_hash', (True, 2, 5))

    # def test_save_cache_data_of_a_function_call_grouped_by_function_name_when_function_directory_doesnt_exist(self):
    #     file_path = os.path.join(Constantes().CACHE_FOLDER_NAME, 'f1', 'func_call_hash')
    #     self.assertFalse(os.path.exists(file_path))

    #     self.storage._save_cache_data_of_a_function_call('func_call_hash', [3.1245123], func_name='f1')
    #     self.assert_cache_data_correctly_inserted('func_call_hash', [3.1245123], func_name='f1')

    # def test_save_cache_data_of_a_function_call_grouped_by_function_name_when_function_directory_already_exists(self):
    #     self.manually_cache_a_record_group_by_function_name('f1', 'func_call_hash', MyClass())

    #     self.storage._save_cache_data_of_a_function_call('func_call_hash', MyClass(), func_name='f1')
    #     self.assert_cache_data_correctly_inserted('func_call_hash', MyClass(), func_name='f1')

class MyClass():
    def __init__(self):
        self.__x = 10
        self.__y = 20