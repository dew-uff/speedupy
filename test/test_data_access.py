from typing import List, Tuple
import unittest, unittest.mock, os, sys, hashlib, mmh3, xxhash, pickle

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from constantes import Constantes
from data_access import get_already_classified_functions, get_id, add_to_metadata, _add_metadata_record, _add_function_params_records, _populate_dont_cache_function_calls_list

class TestDataAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.system("rm -rf .intpy")
        os.mkdir(".intpy")
        cls.create_table_CLASSIFIED_FUNCTIONS()
        cls.create_table_METADATA()
        cls.create_table_FUNCTION_PARAMS()
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
                return_value BLOB NOT NULL,\
                execution_time REAL NOT NULL\
                );"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql)
    
    @classmethod
    def create_table_FUNCTION_PARAMS(cls):
        sql = "CREATE TABLE IF NOT EXISTS FUNCTION_PARAMS (\
                id INTEGER PRIMARY KEY AUTOINCREMENT,\
                metadata_id INTEGER NOT NULL,\
                parameter_value BLOB NOT NULL,\
                parameter_name TEXT,\
                parameter_position INTEGER NOT NULL,\
                FOREIGN KEY (metadata_id) REFERENCES METADATA(id)\
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
        for table in ["CLASSIFIED_FUNCTIONS", "METADATA", "FUNCTION_PARAMS", "DONT_CACHE_FUNCTION_CALLS"]:
            Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(f"DELETE FROM {table} WHERE id IS NOT NULL;")
    
    def assert_METADATA_table_records_are_correct(self, metadata_expected:List[Tuple]):
        sql = f"SELECT id, function_hash, return_value, execution_time FROM METADATA"
        resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
        self.assertEqual(len(resp), len(metadata_expected))
        for i in range(len(resp)):
            self.assertTupleEqual(resp[i], metadata_expected[i])

    def assert_FUNCTION_PARAMS_table_records_are_correct(self, params_expected:List[Tuple]):
        sql = f"SELECT metadata_id, parameter_value, parameter_name, parameter_position FROM FUNCTION_PARAMS"
        resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
        self.assertEqual(len(resp), len(params_expected))
        for i in range(len(resp)):
            self.assertTupleEqual(resp[i], params_expected[i])

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

        fun_source = "print('teste')\nreturn 10"
        fun_hash = xxhash.xxh128_hexdigest(fun_source.encode('utf'))
        fun_args = [1, True]
        fun_kwargs = {'a':10, 'b': 'teste', 'c':[1, -2, 3.26]}
        fun_return = 10
        exec_time = 2.125123
        dict1 = {"hash":fun_hash,
                 "args":fun_args,
                 "kwargs":fun_kwargs,
                 "return":fun_return,
                 "exec_time":exec_time}
        add_to_metadata(fun_hash, fun_args, fun_kwargs, fun_return, exec_time)
        self.assert_addition_to_metadata_is_correct([dict1])

        fun_source = "print('testando')\nprint('\n\n')\nreturn True"
        fun_hash = xxhash.xxh128_hexdigest(fun_source.encode('utf'))
        fun_args = []
        fun_kwargs = {'a':-3, 'c':{1, -2, 3.26}}
        fun_return = True
        exec_time = 5.23151
        dict2 = {"hash":fun_hash,
                 "args":fun_args,
                 "kwargs":fun_kwargs,
                 "return":fun_return,
                 "exec_time":exec_time}
        add_to_metadata(fun_hash, fun_args, fun_kwargs, fun_return, exec_time)
        self.assert_addition_to_metadata_is_correct([dict1, dict2])

    def assert_addition_to_metadata_is_correct(self, dicts:List) -> None:
        self.assertEqual(len(Constantes().METADATA), len(dicts))
        for i in range(len(dicts)):
            self.assertDictEqual(Constantes().METADATA[i], dicts[i])

    def test_add_metadata_record(self):
        self.assert_METADATA_table_records_are_correct([])

        fun_source = "print('testando')\nprint('\n\n')\nreturn 3.7"
        fun_hash = xxhash.xxh128_hexdigest(fun_source.encode('utf'))
        fun_return = 3.7
        exec_time = 2.125123
        id = _add_metadata_record(fun_hash, fun_return, exec_time)
        s_return = pickle.dumps(fun_return)
        metadata_expected = [(id, fun_hash, s_return, exec_time)]
        self.assert_METADATA_table_records_are_correct(metadata_expected)

        fun_source = "print('teste2')\input('\n\n...')\nreturn x ** 3"
        fun_hash = xxhash.xxh128_hexdigest(fun_source.encode('utf'))
        fun_return = 900
        exec_time = 1.1232
        id = _add_metadata_record(fun_hash, fun_return, exec_time)
        s_return = pickle.dumps(fun_return)
        metadata_expected.append((id, fun_hash, s_return, exec_time))
        self.assert_METADATA_table_records_are_correct(metadata_expected)
    
    def test_add_function_params_records_when_function_has_only_args(self):
        #Adding a record on METADATA table, because FUNCTION_PARAMS always references a METADATA record!
        sql = "INSERT INTO METADATA(id, function_hash, return_value, execution_time) VALUES (1, 'sad123asf231', 10, 1.0)"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql)
        _add_function_params_records(1, [1, True, 'abc'], {})
        params_expected = [(1, pickle.dumps(1), None, 0),
                           (1, pickle.dumps(True), None, 1),
                           (1, pickle.dumps('abc'), None, 2)]
        self.assert_FUNCTION_PARAMS_table_records_are_correct(params_expected)

    def test_add_function_params_records_when_function_has_only_kwargs(self):
        #Adding a record on METADATA table, because FUNCTION_PARAMS always references a METADATA record!
        sql = "INSERT INTO METADATA(id, function_hash, return_value, execution_time) VALUES (1, 'sad123asf231', 10, 1.0)"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql)
        _add_function_params_records(1, [], {'a':10, 'b':True, 'c':(1,)})
        params_expected = [(1, pickle.dumps(10), 'a', 0),
                           (1, pickle.dumps(True), 'b', 1),
                           (1, pickle.dumps((1,)), 'c', 2)]
        self.assert_FUNCTION_PARAMS_table_records_are_correct(params_expected)

    def test_add_function_params_records_when_function_has_args_and_kwargs(self):
        #Adding a record on METADATA table, because FUNCTION_PARAMS always references a METADATA record!
        sql = "INSERT INTO METADATA(id, function_hash, return_value, execution_time) VALUES (1, 'sad123asf231', 10, 1.0)"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql)
        _add_function_params_records(1, [{'1':1, '0':0}, True, 'abc'], {'a':-7.5, 'b':[1, 2, 3], 'c':(1,)})
        params_expected = [(1, pickle.dumps({'1':1, '0':0}), None, 0),
                           (1, pickle.dumps(True), None, 1),
                           (1, pickle.dumps('abc'), None, 2),
                           (1, pickle.dumps(-7.5), 'a', 3),
                           (1, pickle.dumps([1, 2, 3]), 'b', 4),
                           (1, pickle.dumps((1,)), 'c', 5)]
        self.assert_FUNCTION_PARAMS_table_records_are_correct(params_expected)
        
    def test_add_function_params_records_when_function_has_one_arg_and_one_kwarg(self):
        #Adding a record on METADATA table, because FUNCTION_PARAMS always references a METADATA record!
        sql = "INSERT INTO METADATA(id, function_hash, return_value, execution_time) VALUES (1, 'sad123asf231', 10, 1.0)"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql)
        _add_function_params_records(1, [True], {'a':-7.5})
        params_expected = [(1, pickle.dumps(True), None, 0),
                           (1, pickle.dumps(-7.5), 'a', 1)]
        self.assert_FUNCTION_PARAMS_table_records_are_correct(params_expected)

    def test_add_function_params_records_when_function_has_multiple_args_and_multiple_kwargs(self):
        #Adding a record on METADATA table, because FUNCTION_PARAMS always references a METADATA record!
        sql = "INSERT INTO METADATA(id, function_hash, return_value, execution_time) VALUES (1, 'sad123asf231', 10, 1.0)"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql)
        _add_function_params_records(1, [True, False, 88], {'a':-7.5, 'b':{1, 2, 10}, 'c':[5, -2]})
        params_expected = [(1, pickle.dumps(True), None, 0),
                           (1, pickle.dumps(False), None, 1),
                           (1, pickle.dumps(88), None, 2),
                           (1, pickle.dumps(-7.5), 'a', 3),
                           (1, pickle.dumps({1, 2, 10}), 'b', 4),
                           (1, pickle.dumps([5, -2]), 'c', 5)]
        self.assert_FUNCTION_PARAMS_table_records_are_correct(params_expected)

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