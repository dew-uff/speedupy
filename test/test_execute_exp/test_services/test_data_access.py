from typing import List, Tuple, Dict
import unittest, unittest.mock, os, sys, hashlib, mmh3, xxhash
from unittest.mock import patch
from pickle import dumps, loads
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from constantes import Constantes
from data_access import get_already_classified_functions, get_id, add_to_metadata, add_to_dont_cache_function_calls, add_to_simulated_function_calls, _save_new_metadata, _save_new_dont_cache_function_calls, _save_new_simulated_function_calls, _populate_dont_cache_function_calls_list, _populate_simulated_function_calls_dict, _populate_function_calls_prov_dict, remove_metadata, get_all_saved_metadata_of_a_function_group_by_function_call_hash, get_function_call_return_freqs, update_function_call_prov
from entities.Metadata import Metadata
from entities.FunctionCallProv import FunctionCallProv

class TestDataAccess(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.system("rm -rf .intpy")
        os.mkdir(".intpy")
        cls.create_table_CLASSIFIED_FUNCTIONS()
        cls.create_table_SIMULATED_FUNCTION_CALLS()
        cls.create_table_METADATA()
        cls.create_table_DONT_CACHE_FUNCTION_CALLS()
        cls.create_table_FUNCTION_CALLS_PROV()

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

    @classmethod
    def create_table_FUNCTION_CALLS_PROV(cls):
        sql = "CREATE TABLE FUNCTION_CALLS_PROV(\
               id INTEGER PRIMARY KEY AUTOINCREMENT,\
               function_call_hash TEXT NOT NULL,\
               outputs BLOB NOT NULL,\
               total_num_exec INTEGER NOT NULL,\
               next_revalidation INTEGER NOT NULL,\
               next_index_weighted_seq INTEGER NOT NULL,\
               mode_rel_freq REAL NOT NULL,\
               mode_output BLOB NOT NULL,\
               weighted_output_seq BLOB NOT NULL,\
               mean_output BLOB NOT NULL,\
               confidence_lv REAL NOT NULL,\
               confidence_low_limit REAL NOT NULL,\
               confidence_up_limit REAL NOT NULL,\
               confidence_error REAL NOT NULL\
               );"
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql)


    def setUp(self):
        Constantes().g_argsp_hash = ["md5"]
        Constantes().NEW_DONT_CACHE_FUNCTION_CALLS = []
        Constantes().NEW_SIMULATED_FUNCTION_CALLS = {}
        Constantes().SIMULATED_FUNCTION_CALLS = {}

    def tearDown(self):
        for table in ["CLASSIFIED_FUNCTIONS", "SIMULATED_FUNCTION_CALLS", "METADATA", "DONT_CACHE_FUNCTION_CALLS", "FUNCTION_CALLS_PROV"]:
            Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(f"DELETE FROM {table} WHERE id IS NOT NULL;")
    
    def assert_metadata_returned_is_correct(self, returned_metadata:Dict[str, List[Metadata]], expected_metadata:Dict[str, Metadata]) -> None:
        self.assertEqual(len(returned_metadata), len(expected_metadata))
        for fc_hash, fc_md in expected_metadata.items():
            for i in range(len(fc_md)):
                self.assertEqual(returned_metadata[fc_hash][i].function_hash, fc_md[i].function_hash)
                self.assertEqual(returned_metadata[fc_hash][i].args, fc_md[i].args)
                self.assertEqual(returned_metadata[fc_hash][i].kwargs, fc_md[i].kwargs)
                self.assertEqual(returned_metadata[fc_hash][i].return_value, fc_md[i].return_value)
                self.assertEqual(returned_metadata[fc_hash][i].execution_time, fc_md[i].execution_time)

    def assert_METADATA_table_records_are_correct(self, metadata_expected:List[Metadata]):
        sql = f"SELECT function_hash, args, kwargs, return_value, execution_time FROM METADATA"
        resp = Constantes().CONEXAO_BANCO.executarComandoSQLSelect(sql)
        self.assertEqual(len(resp), len(metadata_expected))
        for i in range(len(resp)):
            md = metadata_expected[i]
            s_args = dumps(md.args)
            s_kwargs = dumps(md.kwargs)
            s_return = dumps(md.return_value)
            self.assertTupleEqual(resp[i], (md.function_hash, s_args, s_kwargs, s_return, md.execution_time))

    def assert_FUNCTION_CALLS_PROV_equals_expected(self, expected_dict:Dict):
        self.assertListEqual(list(Constantes().NEW_FUNCTION_CALLS_PROV.keys()),
                             list(expected_dict.keys()))
        for fc_hash in expected_dict:
            fc_prov_1 = Constantes().NEW_FUNCTION_CALLS_PROV[fc_hash]
            fc_prov_2 = expected_dict[fc_hash]
            attrs = ['function_call_hash', 'outputs', 'total_num_exec', 'next_revalidation', 'next_index_weighted_seq', 'mode_rel_freq', 'mode_output', 'weighted_output_seq', 'mean_output', 'confidence_lv', 'confidence_low_limit', 'confidence_up_limit', 'confidence_error']
            for a in attrs:
                value1 = getattr(fc_prov_1, a)
                value2 = getattr(fc_prov_2, a)
                if value1 is None:
                    self.assertIsNone(value2)
                elif isinstance(value1, dict):
                    self.assertDictEqual(value1, value2)
                elif isinstance(value1, list):
                    self.assertListEqual(value1, value2)
                else:
                    self.assertEqual(value1, value2)

    def manually_add_metadata(self, metadata:List[Metadata]) -> None:
        sql = "INSERT INTO METADATA(function_hash, args, kwargs, return_value, execution_time) \
                VALUES"
        sql_params = []
        for md in metadata:
            sql += " (?, ?, ?, ?, ?),"
            s_args = dumps(md.args)
            s_kwargs = dumps(md.kwargs)
            s_return = dumps(md.return_value)
            sql_params += [md.function_hash, s_args, s_kwargs, s_return, md.execution_time]
        sql = sql[:-1] #Removendo vírgula final!
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

    def manually_get_id(self, f_source, f_args, f_kwargs, hash_algorithm=['md5']):
        f_call_hash = dumps(f_args) + dumps(f_kwargs)
        f_call_hash = str(f_call_hash) + f_source
        if hash_algorithm == ['md5']:
            f_call_hash = hashlib.md5(f_call_hash.encode('utf')).hexdigest()
        elif hash_algorithm == ['murmur']:
            f_call_hash = hex(mmh3.hash128(f_call_hash.encode('utf')))[2:]
        elif hash_algorithm == ['xxhash']:
            f_call_hash = xxhash.xxh128_hexdigest(f_call_hash.encode('utf'))
        return f_call_hash
    
    def manually_insert_function_calls_prov(self, function_calls_prov:List[FunctionCallProv]):
        sql = "INSERT INTO FUNCTION_CALLS_PROV(function_call_hash, outputs, total_num_exec, next_revalidation, next_index_weighted_seq, mode_rel_freq, mode_output, weighted_output_seq, mean_output, confidence_lv, confidence_low_limit, confidence_up_limit, confidence_error) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        for fp in function_calls_prov:
            sql_params = [fp.function_call_hash, dumps(fp.outputs), fp.total_num_exec, fp.next_revalidation, fp.next_index_weighted_seq, fp.mode_rel_freq, dumps(fp.mode_output), dumps(fp.weighted_output_seq), dumps(fp.mean_output), fp.confidence_lv, fp.confidence_low_limit, fp.confidence_up_limit, fp.confidence_error]
            Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)

    def assert_function_calls_prov_dict_correctly_populated(self, expected_func_calls_prov):
        self.assertEqual(len(Constantes().FUNCTION_CALLS_PROV), len(expected_func_calls_prov))
        for i in range(len(expected_func_calls_prov)):
            p1 = expected_func_calls_prov[i]
            p2 = Constantes().FUNCTION_CALLS_PROV[p1.function_call_hash]
            self.assertEqual(p1.function_call_hash, p2.function_call_hash)
            self.assertEqual(p1.outputs, p2.outputs)
            self.assertEqual(p1.total_num_exec, p2.total_num_exec)
            self.assertEqual(p1.next_revalidation, p2.next_revalidation)
            self.assertEqual(p1.next_index_weighted_seq, p2.next_index_weighted_seq)
            self.assertEqual(p1.mode_rel_freq, p2.mode_rel_freq)
            self.assertEqual(p1.mode_output, p2.mode_output)
            self.assertEqual(p1.weighted_output_seq, p2.weighted_output_seq)
            self.assertEqual(p1.mean_output, p2.mean_output)
            self.assertEqual(p1.confidence_lv, p2.confidence_lv)
            self.assertEqual(p1.confidence_low_limit, p2.confidence_low_limit)
            self.assertEqual(p1.confidence_up_limit, p2.confidence_up_limit)
            self.assertEqual(p1.confidence_error, p2.confidence_error)
    
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
        self.assertDictEqual(Constantes().METADATA, {})

        hash = "hash_func_1"
        args = [1, True]
        kwargs = {'a':10, 'b': 'teste', 'c':[1, -2, 3.26]}
        ret = 10
        exec_time = 2.125123
        f_call_hash_1 = self.manually_get_id(hash, args, kwargs)
        md1 = Metadata(hash, args, kwargs, ret, exec_time)
        add_to_metadata(hash, args, kwargs, ret, exec_time)
        self.assert_metadata_returned_is_correct(Constantes().METADATA, {f_call_hash_1:[md1]})

        hash = 'hash_func_2'
        args = []
        kwargs = {'a':-3, 'c':{1, -2, 3.26}}
        ret = True
        exec_time = 5.23151
        f_call_hash_2 = self.manually_get_id(hash, args, kwargs)
        md2 = Metadata(hash, args, kwargs, ret, exec_time)
        add_to_metadata(hash, args, kwargs, ret, exec_time)
        self.assert_metadata_returned_is_correct(Constantes().METADATA, {f_call_hash_1:[md1], f_call_hash_2:[md2]})

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
        returns_2_freq1 = {10:0.3, 8:0.3, 7:0.4}
        add_to_simulated_function_calls(f_hash, f_args, f_kwargs, returns_2_freq1)
        self.assertDictEqual(Constantes().NEW_SIMULATED_FUNCTION_CALLS, {fc_hash1:returns_2_freq1})

        f_hash = 'hash_func_2'
        f_args = []
        f_kwargs = {'a':-3, 'c':{1, -2, 3.26}}
        fc_hash2 = self.manually_get_id(f_hash, f_args, f_kwargs)
        returns_2_freq2 = {True:0.9, False:0.05, 10:0.05}
        add_to_simulated_function_calls(f_hash, f_args, f_kwargs, returns_2_freq2)
        self.assertDictEqual(Constantes().NEW_SIMULATED_FUNCTION_CALLS,{fc_hash1:returns_2_freq1,
                                                                        fc_hash2:returns_2_freq2})

    def test_save_new_metadata_with_only_one_metadata_record(self):
        f_call_hash = self.manually_get_id('func_hash', [], {})
        md = Metadata('func_hash', [], {}, 3.7, 2.125123)
        Constantes().METADATA = {f_call_hash:[md]}
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_save_new_metadata_when_function_has_only_args(self):
        f_call_hash = self.manually_get_id('func_hash', [1, True, 'abc'], {})
        md = Metadata('func_hash', [1, True, 'abc'], {}, 10, 1.214)
        Constantes().METADATA = {f_call_hash:[md]}
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_save_new_metadata_when_function_has_only_kwargs(self):
        f_call_hash = self.manually_get_id('func_hash', [], {'a':10, 'b':True, 'c':(1,)})
        md = Metadata('func_hash', [], {'a':10, 'b':True, 'c':(1,)}, 10, 1.0)
        Constantes().METADATA = {f_call_hash:[md]}
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_save_new_metadata_when_function_has_args_and_kwargs(self):
        f_call_hash = self.manually_get_id('func_hash', [{'1':1, '0':0}, True, 'abc'], {'a':10, 'b':True, 'c':(1,)})
        md = Metadata('func_hash', [{'1':1, '0':0}, True, 'abc'], {'a':10, 'b':True, 'c':(1,)}, 10, 1.0)
        Constantes().METADATA = {f_call_hash:[md]}
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_save_new_metadata_when_function_has_one_arg_and_one_kwarg(self):
        f_call_hash = self.manually_get_id('func_hash', [True], {'a':-7.5})
        md = Metadata('func_hash', [True], {'a':-7.5}, 10, 1.0)
        Constantes().METADATA = {f_call_hash:[md]}
        _save_new_metadata()
        self.assert_METADATA_table_records_are_correct([md])

    def test_save_new_metadata_when_function_has_many_args_and_kwargs(self):
        f_call_hash = self.manually_get_id('func_hash', [True, False, 88], {'a':-7.5, 'b':{1, 2, 10}, 'c':[5, -2]})
        md = Metadata('func_hash', [True, False, 88], {'a':-7.5, 'b':{1, 2, 10}, 'c':[5, -2]}, 10, 1.0)
        Constantes().METADATA = {f_call_hash:[md]}
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
        self.assertTupleEqual(resp[0], ('fc1_hash', dumps({10:2, 8:3, 7:5})))
        self.assertTupleEqual(resp[1], ('fc2_hash', dumps({True:100, False:3, None:10})))
        self.assertTupleEqual(resp[2], ('fc3_hash', dumps({(1, 2):10, 'TESTE':3})))

    

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
        self.assert_metadata_returned_is_correct(metadata, {f_call_hash:[md3]})
    
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
        self.assert_metadata_returned_is_correct(metadata, {f_call_hash1:[md2, md3],
                                                            f_call_hash2:[md4],
                                                            f_call_hash3:[md5],
                                                            f_call_hash4:[md6]})
    
    def test_remove_metadata_passing_0_metadata(self):
        f_hash = 'func_hash'
        s_args = dumps((1, 2,))
        s_kwargs = dumps({'a':True})
        s_return = dumps(-88)
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
        s_args = dumps((1, 2,))
        s_kwargs = dumps({'a':True})
        s_return = dumps(-88)
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
        returns_2_freq = {10:0.3, False:0.6}
        sql = "INSERT INTO SIMULATED_FUNCTION_CALLS(function_call_hash, returns_2_freq) VALUES (?, ?)"
        sql_params = [hash, dumps(returns_2_freq)]
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)
        _populate_simulated_function_calls_dict()
        self.assertDictEqual(Constantes().SIMULATED_FUNCTION_CALLS, {hash:returns_2_freq})

    def test_populate_simulated_function_calls_dict_when_table_has_many_records(self):
        hash1 = 'func_call_hash1'
        returns_2_freq1 = {10:0.3, False:0.6}
        hash2 = 'func_call_hash2'
        returns_2_freq2 = {1.231:1}
        hash3 = 'func_call_hash3'
        returns_2_freq3 = {5:0.8, 'teste':0.2}
        sql = "INSERT INTO SIMULATED_FUNCTION_CALLS(function_call_hash, returns_2_freq) VALUES (?, ?), (?, ?), (?, ?)"
        sql_params = [hash1, dumps(returns_2_freq1),
                      hash2, dumps(returns_2_freq2),
                      hash3, dumps(returns_2_freq3)]
        Constantes().CONEXAO_BANCO.executarComandoSQLSemRetorno(sql, sql_params)
        _populate_simulated_function_calls_dict()
        self.assertDictEqual(Constantes().SIMULATED_FUNCTION_CALLS, {hash1:returns_2_freq1,
                                                                     hash2:returns_2_freq2,
                                                                     hash3:returns_2_freq3})

    def test_get_function_call_return_freqs_when_function_isnt_simulated(self):
        self.assertIsNone(get_function_call_return_freqs("func_hash", (1,), {'a':False}))        

    def test_get_function_call_return_freqs_when_function_is_simulated(self):
        id = self.manually_get_id("func_hash", (1,), {'a':False})
        Constantes().SIMULATED_FUNCTION_CALLS = {id:{'a':0.5, 'b':0.5}}
        
        ret_2_freq = get_function_call_return_freqs("func_hash", (1,), {'a':False})
        self.assertDictEqual(ret_2_freq, {'a':0.5, 'b':0.5})

    def test_populate_function_calls_prov_dict_when_table_is_empty(self):
        _populate_function_calls_prov_dict()
        self.assertDictEqual(Constantes().FUNCTION_CALLS_PROV, {})

    def test_populate_function_calls_prov_dict_when_table_has_one_record(self):
        provenience = [FunctionCallProv('func_call_hash', {dumps(False): 10}, 10, 3, 0, 1, False, 10*[False], 2, 0.95, 1, 2.27, 0.123)]
        self.manually_insert_function_calls_prov(provenience)
        _populate_function_calls_prov_dict()
        self.assert_function_calls_prov_dict_correctly_populated(provenience)

    def test_populate_function_calls_prov_dict_when_table_has_many_records(self):
        provenience = [FunctionCallProv('func_call_hash', {dumps(False): 10}, 10, 3, 0, 1, False, 10*[False], 2, 0.95, 1, 2.27, 0.123),
                       FunctionCallProv('func_call_hash2', {dumps(12.124): 3}, 3, 3, 0, 1, 12.124, [12.124], 2, 0.80, 123, -3, 0.777),
                       FunctionCallProv('func_call_hash3', {dumps({1, 2, 3}): 1, dumps([1, -6, False]):4}, 5, 3, 0, 0.8, [1, -6, False], 4*[[1, -6, False]] + [{1, 2, 3}], 15, 1, 6, -4, 8)]
        self.manually_insert_function_calls_prov(provenience)
        _populate_function_calls_prov_dict()
        self.assert_function_calls_prov_dict_correctly_populated(provenience)
    
    def test_update_function_call_prov_when_we_have_metadata_from_many_function_calls(self):
        md1 = Metadata('hash_1', (False, 10), {'test':True}, False, 0.523)
        md2 = Metadata('hash_2', (1,), {}, 10.2, 0.523)
        md3 = Metadata('hash_2', (1,), {}, -6, 0.523)
        Constantes().METADATA = {'fc_hash_1': [md1], 'fc_hash_2': [md2, md3]}
        Constantes().FUNCTION_CALLS_PROV = {}
        Constantes().NEW_FUNCTION_CALLS_PROV = {}
        update_function_call_prov('fc_hash_2')
        new_fc_prov = FunctionCallProv('fc_hash_2', outputs={dumps(10.2):1, dumps(-6):1}, total_num_exec=2)
        self.assert_FUNCTION_CALLS_PROV_equals_expected({'fc_hash_2': new_fc_prov})

    def test_update_function_call_prov_when_function_call_prov_is_new(self):
        md = Metadata('hash_3', (1,), {}, 10, 0.523)
        Constantes().METADATA = {'fc_hash_3': [md]}
        Constantes().FUNCTION_CALLS_PROV = {'fc_hash_1': FunctionCallProv('fc_hash_1'),
                                            'fc_hash_2': FunctionCallProv('fc_hash_2')}
        Constantes().NEW_FUNCTION_CALLS_PROV = {}
        update_function_call_prov('fc_hash_3')
        new_fc_prov = FunctionCallProv('fc_hash_3', outputs={dumps(10):1}, total_num_exec=1)
        self.assert_FUNCTION_CALLS_PROV_equals_expected({'fc_hash_3': new_fc_prov})

    def test_update_function_call_prov_when_function_call_prov_already_exists_but_was_not_updated_yet(self):
        md = Metadata('hash_1', (1,), {}, False, 0.523)
        Constantes().METADATA = {'fc_hash_1': [md]}
        Constantes().FUNCTION_CALLS_PROV = {'fc_hash_1': FunctionCallProv('fc_hash_1', outputs={dumps(False):10}, total_num_exec=10),
                                            'fc_hash_2': FunctionCallProv('fc_hash_2')}
        Constantes().NEW_FUNCTION_CALLS_PROV = {}
        update_function_call_prov('fc_hash_1')
        new_fc_prov = FunctionCallProv('fc_hash_1', outputs={dumps(False):11}, total_num_exec=11)
        self.assert_FUNCTION_CALLS_PROV_equals_expected({'fc_hash_1': new_fc_prov})

    def test_update_function_call_prov_when_function_call_prov_already_exists_and_it_was_already_updated(self):
        md = Metadata('hash_2', (1,), {}, False, 0.523)
        Constantes().METADATA = {'fc_hash_2': [md]}
        Constantes().FUNCTION_CALLS_PROV = {'fc_hash_1': FunctionCallProv('fc_hash_1', outputs={dumps(False):10}, total_num_exec=10)}
        Constantes().NEW_FUNCTION_CALLS_PROV = {'fc_hash_2': FunctionCallProv('fc_hash_2', outputs={dumps(2.6):3}, total_num_exec=3)}
        update_function_call_prov('fc_hash_2')
        new_fc_prov = FunctionCallProv('fc_hash_2', outputs={dumps(2.6):3, dumps(False):1}, total_num_exec=4)
        self.assert_FUNCTION_CALLS_PROV_equals_expected({'fc_hash_2': new_fc_prov})

    def test_update_function_call_prov_when_metadata_output_is_new(self):
        md = Metadata('hash_1', (1,), {}, 4, 0.523)
        Constantes().METADATA = {'fc_hash_1': [md]}
        Constantes().FUNCTION_CALLS_PROV = {'fc_hash_1': FunctionCallProv('fc_hash_1', outputs={dumps(False):10}, total_num_exec=10),
                                            'fc_hash_2': FunctionCallProv('fc_hash_2')}
        Constantes().NEW_FUNCTION_CALLS_PROV = {}
        update_function_call_prov('fc_hash_1')
        new_fc_prov = FunctionCallProv('fc_hash_1', outputs={dumps(False):10, dumps(4):1}, total_num_exec=11)
        self.assert_FUNCTION_CALLS_PROV_equals_expected({'fc_hash_1': new_fc_prov})

    def test_update_function_call_prov_when_metadata_output_already_exists(self):
        md = Metadata('hash_1', (1,), {}, 'My result', 0.523)
        Constantes().METADATA = {'fc_hash_1': [md]}
        Constantes().FUNCTION_CALLS_PROV = {'fc_hash_1': FunctionCallProv('fc_hash_1', outputs={dumps('My result'):2}, total_num_exec=2),
                                            'fc_hash_2': FunctionCallProv('fc_hash_2')}
        Constantes().NEW_FUNCTION_CALLS_PROV = {}
        update_function_call_prov('fc_hash_1')
        new_fc_prov = FunctionCallProv('fc_hash_1', outputs={dumps('My result'):3}, total_num_exec=3)
        self.assert_FUNCTION_CALLS_PROV_equals_expected({'fc_hash_1': new_fc_prov})

if __name__ == '__main__':
    unittest.main()