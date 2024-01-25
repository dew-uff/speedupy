from typing import List, Tuple, Dict
import unittest, unittest.mock, os, sys, hashlib, mmh3, xxhash, pickle

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from constantes import Constantes
from data_access import get_already_classified_functions, get_id, add_to_metadata, add_to_dont_cache_function_calls, add_to_simulated_function_calls, _save_new_metadata, _save_new_dont_cache_function_calls, _save_new_simulated_function_calls, _populate_dont_cache_function_calls_list, _populate_simulated_function_calls_dict, remove_metadata, get_all_saved_metadata_of_a_function_group_by_function_call_hash
from entities.Metadata import Metadata

class TestDataAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.system("rm -rf .intpy")
        os.mkdir(".intpy")
        cls.create_table_CLASSIFIED_FUNCTIONS()
        cls.create_table_SIMULATED_FUNCTION_CALLS()
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
    def create_table_SIMULATED_FUNCTION_CALLS(cls):
        sql = "CREATE TABLE IF NOT EXISTS SIMULATED_FUNCTION_CALLS (\
               id INTEGER PRIMARY KEY AUTOINCREMENT,\
               function_call_hash TEXT NOT NULL,\
               returns_2_freq BLOB NOT NULL\
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

    def setUp(self):
        Constantes().g_argsp_hash = ["md5"]
        Constantes().NEW_DONT_CACHE_FUNCTION_CALLS = []
        Constantes().NEW_SIMULATED_FUNCTION_CALLS = {}
        Constantes().SIMULATED_FUNCTION_CALLS = {}

    def tearDown(self):
        for table in ["CLASSIFIED_FUNCTIONS", "SIMULATED_FUNCTION_CALLS", "METADATA", "DONT_CACHE_FUNCTION_CALLS"]:
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

    def manually_get_id(self, f_source, f_args, f_kwargs, hash_algorithm=['md5']):
        f_call_hash = pickle.dumps(f_args) + pickle.dumps(f_kwargs)
        f_call_hash = str(f_call_hash) + f_source
        if hash_algorithm == ['md5']:
            f_call_hash = hashlib.md5(f_call_hash.encode('utf')).hexdigest()
        elif hash_algorithm == ['murmur']:
            f_call_hash = hex(mmh3.hash128(f_call_hash.encode('utf')))[2:]
        elif hash_algorithm == ['xxhash']:
            f_call_hash = xxhash.xxh128_hexdigest(f_call_hash.encode('utf'))
        return f_call_hash
    
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
        expected = self.manually_get_id(source, [1, 5], {'z':-12.5})
        self.assertEqual(hash, expected)

    def test_get_id_with_hash_xxhash(self):
        Constantes().g_argsp_hash = ['xxhash']
        source = 'print("Essa é uma função de teste!")\nreturn x ** y / z'
        hash = get_id(source, [1, 5], {'z':-12.5})
        expected = self.manually_get_id(source, [1, 5], {'z':-12.5}, hash_algorithm=['xxhash'])
        self.assertEqual(hash, expected)

    def test_get_id_with_hash_murmur(self):
        Constantes().g_argsp_hash = ['murmur']
        source = 'print("Essa é uma função de teste!")\nreturn x ** y / z'
        hash = get_id(source, [1, 5], {'z':-12.5})
        expected = self.manually_get_id(source, [1, 5], {'z':-12.5}, hash_algorithm=['murmur'])
        self.assertEqual(hash, expected)
        
    def test_get_id_without_fun_args(self):
        Constantes().g_argsp_hash = ['xxhash']
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'
        hash = get_id(source, fun_kwargs={'z':-12.5})
        expected = self.manually_get_id(source, [], {'z':-12.5}, hash_algorithm=['xxhash'])
        self.assertEqual(hash, expected)

    def test_get_id_without_fun_kwargs(self):
        Constantes().g_argsp_hash = ['md5']
        source = 'print("Testando!")\nos.path.exists("/")\nrandom.randint()\nreturn x + y / -z'
        hash = get_id(source, fun_args=[-1.227, 0])
        expected = self.manually_get_id(source, [-1.227, 0], {})
        self.assertEqual(hash, expected)

    def test_get_id_only_with_fun_source(self):
        Constantes().g_argsp_hash = ['murmur']
        source = 'print("Testando!")\nreturn x / y ** 2'
        hash = get_id(source)
        expected = self.manually_get_id(source, [], {}, hash_algorithm=['murmur'])
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

    def test_add_to_dont_cache_function_calls(self):
        self.assertListEqual(Constantes().NEW_DONT_CACHE_FUNCTION_CALLS, [])
        f_hash = "hash_func_1"
        f_args = [1, True]
        f_kwargs = {'a':10, 'b': 'teste', 'c':[1, -2, 3.26]}
        fc_hash1 = self.manually_get_id(f_hash, f_args, f_kwargs)
        add_to_dont_cache_function_calls(f_hash, f_args, f_kwargs)
        self.assertListEqual(Constantes().NEW_DONT_CACHE_FUNCTION_CALLS, [fc_hash1])

        f_hash = 'hash_func_2'
        f_args = []
        f_kwargs = {'a':-3, 'c':{1, -2, 3.26}}
        fc_hash2 = self.manually_get_id(f_hash, f_args, f_kwargs)
        add_to_dont_cache_function_calls(f_hash, f_args, f_kwargs)
        self.assertListEqual(Constantes().NEW_DONT_CACHE_FUNCTION_CALLS, [fc_hash1, fc_hash2])

    def test_add_to_simulated_function_calls(self):
        self.assertDictEqual(Constantes().NEW_SIMULATED_FUNCTION_CALLS, {})
        f_hash = "hash_func_1"
        f_args = [1, True]
        f_kwargs = {'a':10, 'b': 'teste', 'c':[1, -2, 3.26]}
        fc_hash1 = self.manually_get_id(f_hash, f_args, f_kwargs)
        returns_2_freq1 = {10:2, 8:3, 7:5}
        add_to_simulated_function_calls(f_hash, f_args, f_kwargs, returns_2_freq1)
        self.assertDictEqual(Constantes().NEW_SIMULATED_FUNCTION_CALLS, {fc_hash1:returns_2_freq1})

        f_hash = 'hash_func_2'
        f_args = []
        f_kwargs = {'a':-3, 'c':{1, -2, 3.26}}
        fc_hash2 = self.manually_get_id(f_hash, f_args, f_kwargs)
        returns_2_freq2 = {True:100, False:3, None:10}
        add_to_simulated_function_calls(f_hash, f_args, f_kwargs, returns_2_freq2)
        self.assertDictEqual(Constantes().NEW_SIMULATED_FUNCTION_CALLS,{fc_hash1:returns_2_freq1,
                                                                        fc_hash2:returns_2_freq2})

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

    def test_save_new_dont_cache_function_calls_with_0_new_dont_cache_function_calls(self):
        Constantes().NEW_DONT_CACHE_FUNCTION_CALLS = []
        _save_new_dont_cache_function_calls()
        sql = 'SELECT function_call_hash FROM DONT_CACHE_FUNCTION_CALLS'
        resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
        self.assertListEqual(resp, [])
        
    def test_save_new_dont_cache_function_calls_with_3_new_dont_cache_function_calls(self):
        Constantes().NEW_DONT_CACHE_FUNCTION_CALLS = ['fc1_hash', 'fc2_hash', 'fc3_hash']
        _save_new_dont_cache_function_calls()
        sql = 'SELECT function_call_hash FROM DONT_CACHE_FUNCTION_CALLS'
        resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
        self.assertEqual(len(resp), 3)
        self.assertEqual(resp[0][0], 'fc1_hash')
        self.assertEqual(resp[1][0], 'fc2_hash')
        self.assertEqual(resp[2][0], 'fc3_hash')

    def test_save_new_simulated_function_calls_with_0_new_simulated_function_calls(self):
        Constantes().NEW_SIMULATED_FUNCTION_CALLS = {}
        _save_new_simulated_function_calls()
        sql = 'SELECT function_call_hash, returns_2_freq FROM SIMULATED_FUNCTION_CALLS'
        resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
        self.assertListEqual(resp, [])
        
    def test_save_new_simulated_function_calls_with_3_new_simulated_function_calls(self):
        Constantes().NEW_SIMULATED_FUNCTION_CALLS = {'fc1_hash':{10:2, 8:3, 7:5},
                                                     'fc2_hash':{True:100, False:3, None:10},
                                                     'fc3_hash':{(1, 2):10, 'TESTE':3}}
        _save_new_simulated_function_calls()
        sql = 'SELECT function_call_hash, returns_2_freq FROM SIMULATED_FUNCTION_CALLS'
        resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
        self.assertEqual(len(resp), 3)
        self.assertTupleEqual(resp[0], ('fc1_hash', pickle.dumps({10:2, 8:3, 7:5})))
        self.assertTupleEqual(resp[1], ('fc2_hash', pickle.dumps({True:100, False:3, None:10})))
        self.assertTupleEqual(resp[2], ('fc3_hash', pickle.dumps({(1, 2):10, 'TESTE':3})))

    

    def test_get_all_saved_metadata_of_a_function_when_metadata_table_is_empty(self):
        metadata = get_all_saved_metadata_of_a_function_group_by_function_call_hash("func_hash")
        self.assertDictEqual(metadata, {})

    def test_get_all_saved_metadata_of_a_function_when_there_is_only_metadata_for_other_functions(self):
        md1 = Metadata('hash1', [10, True], {'text':'Teste'}, True, 10.2)
        md2 = Metadata('hash2', [-3.2, (1,), 'teste'], {'content':'Testando'}, 'My return!', 3.0)
        self.manually_add_metadata([md1, md2])
        metadata = get_all_saved_metadata_of_a_function_group_by_function_call_hash("func_hash")
        self.assertDictEqual(metadata, {})

    def test_get_all_saved_metadata_of_a_function_when_there_is_one_metadata_record_and_the_function_has_args_and_kwargs(self):
        md1 = Metadata('hash1', [10, True], {'text':'Teste'}, True, 10.2)
        md2 = Metadata('hash2', [-3.2, (1,), 'teste'], {'content':'Testando'}, 'My return!', 3.0)
        md3 = Metadata('func_hash', [-3.2, [(1,)], {'teste'}], {'content':False}, -23.124, 12.1234)
        self.manually_add_metadata([md1, md2, md3])
        metadata = get_all_saved_metadata_of_a_function_group_by_function_call_hash("func_hash")
        
        f_call_hash = self.manually_get_id('func_hash', [-3.2, [(1,)], {'teste'}], {'content':False})
        self.assertEqual(len(metadata), 1)
        self.assertIn(f_call_hash, metadata)
        self.assert_metadata_returned_is_correct(metadata[f_call_hash], [md3])
    
    def test_get_all_saved_metadata_of_a_function_when_there_are_many_metadata_records_of_different_function_calls_for_the_function_passed(self):
        md1 = Metadata('hash1', [10, True], {'text':'Teste'}, True, 10.2)
        md2 = Metadata('func_hash', [1, True], {'content':'Teste'}, 'My return!', 3.0)
        md3 = Metadata('func_hash', [1, True], {'content':'Teste'}, -23.124, 12.1234)
        md4 = Metadata('func_hash', [2, False], {'content':'Teste2'}, 10, 20.155)
        md5 = Metadata('func_hash', [], {'x':20}, -2, 0.123)
        md6 = Metadata('func_hash', [0], {}, 400, 56.23)
        self.manually_add_metadata([md1, md2, md3, md4, md5, md6])
        metadata = get_all_saved_metadata_of_a_function_group_by_function_call_hash("func_hash")

        f_call_hash1 = self.manually_get_id('func_hash', [1, True], {'content':'Teste'})
        f_call_hash2 = self.manually_get_id('func_hash', [2, False], {'content':'Teste2'})
        f_call_hash3 = self.manually_get_id('func_hash', [], {'x':20})
        f_call_hash4 = self.manually_get_id('func_hash', [0], {})
        expected_f_call_hashes = [f_call_hash1, f_call_hash2, f_call_hash3, f_call_hash4]
        self.assertEqual(len(metadata), 4)
        self.assertListEqual(list(metadata.keys()), expected_f_call_hashes)
        self.assert_metadata_returned_is_correct(metadata[f_call_hash1], [md2, md3])
        self.assert_metadata_returned_is_correct(metadata[f_call_hash2], [md4])
        self.assert_metadata_returned_is_correct(metadata[f_call_hash3], [md5])
        self.assert_metadata_returned_is_correct(metadata[f_call_hash4], [md6])
    
    def test_remove_metadata_passing_0_metadata(self):
        f_hash = 'func_hash'
        s_args = pickle.dumps((1, 2,))
        s_kwargs = pickle.dumps({'a':True})
        s_return = pickle.dumps(-88)
        sql = 'INSERT INTO METADATA(id, function_hash, args, kwargs, return_value, execution_time) VALUES '
        sql_params = []
        for i in range(3):
            sql += '(?, ?, ?, ?, ?, ?),'
            sql_params += [i+1, f_hash, s_args, s_kwargs, s_return, 123.123]
        sql = sql[:-1]
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

        remove_metadata([])
        resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect('SELECT id FROM METADATA')
        self.assertEqual(resp[0][0], 1)
        self.assertEqual(resp[1][0], 2)
        self.assertEqual(resp[2][0], 3)

    def test_remove_metadata_passing_3_metadata(self):
        f_hash = 'func_hash'
        s_args = pickle.dumps((1, 2,))
        s_kwargs = pickle.dumps({'a':True})
        s_return = pickle.dumps(-88)
        sql = 'INSERT INTO METADATA(id, function_hash, args, kwargs, return_value, execution_time) VALUES '
        sql_params = []
        for i in range(6):
            sql += '(?, ?, ?, ?, ?, ?),'
            sql_params += [i+1, f_hash, s_args, s_kwargs, s_return, 123.123]
        sql = sql[:-1]
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

        md1 = Metadata(f_hash, (1, 2,), {'a':True}, -88, 123.123)
        md1._Metadata__id = 1
        md3 = Metadata(f_hash, (1, 2,), {'a':True}, -88, 123.123)
        md3._Metadata__id = 3
        md5 = Metadata(f_hash, (1, 2,), {'a':True}, -88, 123.123)
        md5._Metadata__id = 5
        remove_metadata([md1, md3, md5])
        resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect('SELECT id FROM METADATA')
        self.assertEqual(resp[0][0], 2)
        self.assertEqual(resp[1][0], 4)
        self.assertEqual(resp[2][0], 6)

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

    def test_populate_simulated_function_calls_dict_when_table_is_empty(self):
        _populate_simulated_function_calls_dict()
        self.assertDictEqual(Constantes().SIMULATED_FUNCTION_CALLS, {})

    def test_populate_simulated_function_calls_dict_when_table_has_one_record(self):
        hash = 'func_call_hash'
        returns_2_freq = {10:3, False:4}
        sql = "INSERT INTO SIMULATED_FUNCTION_CALLS(function_call_hash, returns_2_freq) VALUES (?, ?)"
        sql_params = [hash, pickle.dumps(returns_2_freq)]
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)
        _populate_simulated_function_calls_dict()
        self.assertDictEqual(Constantes().SIMULATED_FUNCTION_CALLS, {hash:returns_2_freq})

    def test_populate_simulated_function_calls_dict_when_table_has_many_records(self):
        hash1 = 'func_call_hash1'
        returns_2_freq1 = {10:3, False:4}
        hash2 = 'func_call_hash2'
        returns_2_freq2 = {1.231:4}
        hash3 = 'func_call_hash3'
        returns_2_freq3 = {5:3, 'teste':4}
        sql = "INSERT INTO SIMULATED_FUNCTION_CALLS(function_call_hash, returns_2_freq) VALUES (?, ?), (?, ?), (?, ?)"
        sql_params = [hash1, pickle.dumps(returns_2_freq1),
                      hash2, pickle.dumps(returns_2_freq2),
                      hash3, pickle.dumps(returns_2_freq3)]
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)
        _populate_simulated_function_calls_dict()
        self.assertDictEqual(Constantes().SIMULATED_FUNCTION_CALLS, {hash1:returns_2_freq1,
                                                                     hash2:returns_2_freq2,
                                                                     hash3:returns_2_freq3})

if __name__ == '__main__':
    unittest.main()