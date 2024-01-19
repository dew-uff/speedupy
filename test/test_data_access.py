from typing import List, Tuple
import unittest, unittest.mock, os, sys, hashlib, mmh3, xxhash, pickle

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from constantes import Constantes
from data_access import get_already_classified_functions, get_id, add_to_metadata, _save_new_metadata, _populate_dont_cache_function_calls_list, get_all_saved_metadata_of_a_function
from entities.Metadata import Metadata

class TestDataAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.system("rm -rf .intpy")
        os.mkdir(".intpy")
        cls.create_table_CLASSIFIED_FUNCTIONS()
        cls.create_table_METADATA()
        cls.create_table_DONT_CACHE_FUNCTION_CALLS()

    @classmethod
    def tearDownClass(cls):
        Constantes().CONEXAO_BANCO.fecharConexao()
        os.system("rm -rf .intpy")
    
    @classmethod
    def create_table_CLASSIFIED_FUNCTIONS(cls):
        sql = "CREATE TABLE IF NOT EXISTS CLASSIFIED_FUNCTIONS (\
               id INTEGER PRIMARY KEY AUTOINCREMENT,\
               function_hash TEXT NOT NULL,\
               classification TEXT NOT NULL\
               );"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql)
    
    @classmethod
    def create_table_METADATA(cls):
        sql = "CREATE TABLE IF NOT EXISTS METADATA (\
                id INTEGER PRIMARY KEY AUTOINCREMENT,\
                function_hash TEXT NOT NULL,\
                args BLOB NOT NULL,\
                kwargs BLOB NOT NULL,\
                return_value BLOB NOT NULL,\
                execution_time REAL NOT NULL\
                );"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql)
    
    @classmethod
    def create_table_DONT_CACHE_FUNCTION_CALLS(cls):
        sql = "CREATE TABLE IF NOT EXISTS DONT_CACHE_FUNCTION_CALLS (\
                id INTEGER PRIMARY KEY AUTOINCREMENT,\
                function_call_hash TEXT NOT NULL\
                );"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql)

    def tearDown(self):
        for table in ["CLASSIFIED_FUNCTIONS", "METADATA", "DONT_CACHE_FUNCTION_CALLS"]:
            Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(f"DELETE FROM {table} WHERE id IS NOT NULL;")
    
    def assert_metadata_returned_is_correct(self, returned_metadata:List[Metadata], expected_metadata:List[Metadata]) -> None:
        self.assertEqual(len(returned_metadata), len(expected_metadata))
        for i in range(len(expected_metadata)):
            self.assertEqual(returned_metadata[i].function_hash, expected_metadata[i].function_hash)
            self.assertEqual(returned_metadata[i].args, expected_metadata[i].args)
            self.assertEqual(returned_metadata[i].kwargs, expected_metadata[i].kwargs)
            self.assertEqual(returned_metadata[i].return_value, expected_metadata[i].return_value)
            self.assertEqual(returned_metadata[i].execution_time, expected_metadata[i].execution_time)

    def assert_METADATA_table_records_are_correct(self, metadata_expected:List[Metadata]):
        sql = f"SELECT function_hash, args, kwargs, return_value, execution_time FROM METADATA"
        resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
        self.assertEqual(len(resp), len(metadata_expected))
        for i in range(len(resp)):
            md = metadata_expected[i]
            s_args = pickle.dumps(md.args)
            s_kwargs = pickle.dumps(md.kwargs)
            s_return = pickle.dumps(md.return_value)
            self.assertTupleEqual(resp[i], (md.function_hash, s_args, s_kwargs, s_return, md.execution_time))

    def test_get_already_classified_functions_with_zero_classified_functions(self):
        functions = get_already_classified_functions()
        self.assertDictEqual({}, functions)

    def test_get_already_classified_functions_with_CACHE_and_DONT_CACHE_functions(self):
        f1 = hash('def f1():\n\treturn "f1"')
        f2 = hash('def f2(a):\n\treturn a ** 2')
        f3 = hash('def f3(x, y):\n\treturn x/y')
        f4 = hash('def f4():\n\treturn "f4"')
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(f"INSERT INTO CLASSIFIED_FUNCTIONS(function_hash, classification) VALUES ('{f1}', 'CACHE'), ('{f2}', 'CACHE'), ('{f3}', 'DONT_CACHE'), ('{f4}', 'DONT_CACHE');")

        functions = get_already_classified_functions()
        expected_functions = {f'{f1}':'CACHE',
                              f'{f2}':'CACHE',
                              f'{f3}':'DONT_CACHE',
                              f'{f4}':'DONT_CACHE'}
        self.assertDictEqual(expected_functions, functions)

    def test_get_id_with_hash_md5(self):
        Constantes().g_argsp_hash = ['md5']
        source = 'print("Essa é uma função de teste!")\nreturn x ** y / z'
        hash = get_id(source, [1, 5], {'z':-12.5})
        expected = b""
        for elem in [1, 5, 'z', -12.5]:
            expected += pickle.dumps(elem)
        expected = str(expected) + source
        expected = hashlib.md5(expected.encode('utf')).hexdigest()
        self.assertEqual(hash, expected)

    def test_get_id_with_hash_xxhash(self):
        Constantes().g_argsp_hash = ['xxhash']
        source = 'print("Essa é uma função de teste!")\nreturn x ** y / z'
        hash = get_id(source, [1, 5], {'z':-12.5})
        expected = b""
        for elem in [1, 5, 'z', -12.5]:
            expected += pickle.dumps(elem)
        expected = str(expected) + source
        expected = xxhash.xxh128_hexdigest(expected.encode('utf'))
        self.assertEqual(hash, expected)

    def test_get_id_with_hash_murmur(self):
        Constantes().g_argsp_hash = ['murmur']
        source = 'print("Essa é uma função de teste!")\nreturn x ** y / z'
        hash = get_id(source, [1, 5], {'z':-12.5})
        expected = b""
        for elem in [1, 5, 'z', -12.5]:
            expected += pickle.dumps(elem)
        expected = str(expected) + source
        expected = hex(mmh3.hash128(expected.encode('utf')))[2:]
        self.assertEqual(hash, expected)
        
    def test_get_id_without_fun_args(self):
        Constantes().g_argsp_hash = ['xxhash']
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'
        hash = get_id(source, fun_kwargs={'z':-12.5})
        expected = b""
        for elem in ['z', -12.5]:
            expected += pickle.dumps(elem)
        expected = str(expected) + source
        expected = xxhash.xxh128_hexdigest(expected.encode('utf'))
        self.assertEqual(hash, expected)

    def test_get_id_without_fun_kwargs(self):
        Constantes().g_argsp_hash = ['md5']
        source = 'print("Testando!")\nos.path.exists("/")\nrandom.randint()\nreturn x + y / -z'
        hash = get_id(source, fun_args=[-1.227, 0])
        expected = b""
        for elem in [-1.227, 0]:
            expected += pickle.dumps(elem)
        expected = str(expected) + source
        expected = hashlib.md5(expected.encode('utf')).hexdigest()
        self.assertEqual(hash, expected)

    def test_get_id_only_with_fun_source(self):
        Constantes().g_argsp_hash = ['murmur']
        source = 'print("Testando!")\nreturn x / y ** 2'
        hash = get_id(source)
        expected = b""
        expected = str(expected) + source
        expected = hex(mmh3.hash128(expected.encode('utf')))[2:]
        self.assertEqual(hash, expected)

    def test_add_to_metadata(self):
        self.assertListEqual(Constantes().METADATA, [])
        hash = "hash_func_1"
        args = [1, True]
        kwargs = {'a':10, 'b': 'teste', 'c':[1, -2, 3.26]}
        ret = 10
        exec_time = 2.125123
        md1 = Metadata(hash, args, kwargs, ret, exec_time)
        add_to_metadata(hash, args, kwargs, ret, exec_time)
        self.assert_metadata_returned_is_correct(Constantes().METADATA, [md1])

        hash = 'hash_func_2'
        args = []
        kwargs = {'a':-3, 'c':{1, -2, 3.26}}
        ret = True
        exec_time = 5.23151
        md2 = Metadata(hash, args, kwargs, ret, exec_time)
        add_to_metadata(hash, args, kwargs, ret, exec_time)
        self.assert_metadata_returned_is_correct(Constantes().METADATA, [md1, md2])

    def test_save_new_metadata_with_only_one_metadata_record(self):
        md = Metadata('func_hash', [], {}, 3.7, 2.125123)
        Constantes().METADATA = [md]
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_save_new_metadata_when_function_has_only_args(self):
        md = Metadata('func_hash', [1, True, 'abc'], {}, 10, 1.214)
        Constantes().METADATA = [md]
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_save_new_metadata_when_function_has_only_kwargs(self):
        md = Metadata('func_hash', [], {'a':10, 'b':True, 'c':(1,)}, 10, 1.0)
        Constantes().METADATA = [md]
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_save_new_metadata_when_function_has_args_and_kwargs(self):
        md = Metadata('func_hash', [{'1':1, '0':0}, True, 'abc'], {'a':10, 'b':True, 'c':(1,)}, 10, 1.0)
        Constantes().METADATA = [md]
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_save_new_metadata_when_function_has_one_arg_and_one_kwarg(self):
        md = Metadata('func_hash', [True], {'a':-7.5}, 10, 1.0)
        Constantes().METADATA = [md]
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_save_new_metadata_when_function_has_many_args_and_kwargs(self):
        md = Metadata('func_hash', [True, False, 88], {'a':-7.5, 'b':{1, 2, 10}, 'c':[5, -2]}, 10, 1.0)
        Constantes().METADATA = [md]
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_get_all_saved_metadata_of_a_function_when_metadata_tables_are_empty(self):
        metadata = get_all_saved_metadata_of_a_function("func_hash")
        self.assertListEqual(metadata, [])

    def manually_add_metadata(self, metadata:List[Metadata]) -> None:
        sql = "INSERT INTO METADATA(function_hash, args, kwargs, return_value, execution_time) \
                VALUES"
        sql_params = []
        for md in metadata:
            sql += " (?, ?, ?, ?, ?),"
            s_args = pickle.dumps(md.args)
            s_kwargs = pickle.dumps(md.kwargs)
            s_return = pickle.dumps(md.return_value)
            sql_params += [md.function_hash, s_args, s_kwargs, s_return, md.execution_time]
        sql = sql[:-1] #Removendo vírgula final!
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

    def test_get_all_saved_metadata_of_a_function_when_there_is_only_metadata_for_other_functions(self):
        md1 = Metadata('hash1', [10, True], {'text':'Teste'}, True, 10.2)
        md2 = Metadata('hash2', [-3.2, (1,), 'teste'], {'content':'Testando'}, 'My return!', 3.0)
        self.manually_add_metadata([md1, md2])
        metadata = get_all_saved_metadata_of_a_function("func_hash")
        self.assertListEqual(metadata, [])
    
    def test_get_all_saved_metadata_of_a_function_when_there_is_one_metadata_record_and_the_function_has_args_and_kwargs(self):
        md1 = Metadata('hash1', [10, True], {'text':'Teste'}, True, 10.2)
        md2 = Metadata('hash2', [-3.2, (1,), 'teste'], {'content':'Testando'}, 'My return!', 3.0)
        md3 = Metadata('func_hash', [-3.2, [(1,)], {'teste'}], {'content':False}, -23.124, 12.1234)
        self.manually_add_metadata([md1, md2, md3])
        metadata = get_all_saved_metadata_of_a_function("func_hash")
        self.assert_metadata_returned_is_correct(metadata, [md3])
    
    def test_get_all_saved_metadata_of_a_function_when_there_are_many_metadata_records_of_different_function_calls_for_the_function_passed(self):
        md1 = Metadata('hash1', [10, True], {'text':'Teste'}, True, 10.2)
        md2 = Metadata('func_hash', [1, True], {'content':'Teste'}, 'My return!', 3.0)
        md3 = Metadata('func_hash', [1, True], {'content':'Teste'}, -23.124, 12.1234)
        md4 = Metadata('func_hash', [2, False], {'content':'Teste2'}, 10, 20.155)
        md5 = Metadata('func_hash', [], {'x':20}, -2, 0.123)
        md6 = Metadata('func_hash', [0], {}, 400, 56.23)
        self.manually_add_metadata([md1, md2, md3, md4, md5, md6])
        metadata = get_all_saved_metadata_of_a_function("func_hash")
        self.assert_metadata_returned_is_correct(metadata, [md2, md3, md4, md5, md6])

    def test_populate_dont_cache_function_calls_dictionay_when_table_is_empty(self):
        _populate_dont_cache_function_calls_list()
        self.assertListEqual(Constantes().DONT_CACHE_FUNCTION_CALLS, [])

    def test_populate_dont_cache_function_calls_dictionay_when_table_has_one_record(self):
        hash = xxhash.xxh128_hexdigest("String de teste 1".encode('utf'))
        sql = "INSERT INTO DONT_CACHE_FUNCTION_CALLS(function_call_hash) VALUES (?)"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, [hash])
        _populate_dont_cache_function_calls_list()
        self.assertListEqual(Constantes().DONT_CACHE_FUNCTION_CALLS, [hash])

    def test_populate_dont_cache_function_calls_dictionay_when_table_has_many_records(self):
        hash1 = xxhash.xxh128_hexdigest("String de teste 1".encode('utf'))
        hash2 = xxhash.xxh128_hexdigest("Testando....".encode('utf'))
        hash3 = xxhash.xxh128_hexdigest("Outra mensagem!!!!".encode('utf'))
        sql = "INSERT INTO DONT_CACHE_FUNCTION_CALLS(function_call_hash) VALUES (?), (?), (?)"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, [hash1, hash2, hash3])
        _populate_dont_cache_function_calls_list()
        self.assertListEqual(Constantes().DONT_CACHE_FUNCTION_CALLS, [hash1, hash2, hash3])

if __name__ == '__main__':
    unittest.main()