import unittest, unittest.mock, os, sys, hashlib, mmh3, xxhash
from unittest.mock import patch
from pickle import dumps

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.DataAccess import DataAccess, get_id
from execute_exp.SpeeduPySettings import SpeeduPySettings
from entities.Metadata import Metadata

class TestDataAccess(unittest.TestCase):
    def setUp(self):
        SpeeduPySettings().hash = ["md5"]
        self.dataAccess = DataAccess()
        
    def tearDown(self) -> None:
        self.dataAccess._DataAccess__METADATA = {}

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
    
    def test_get_id_with_hash_md5(self):
        SpeeduPySettings().hash = ['md5']
        source = 'print("Essa é uma função de teste!")\nreturn x ** y / z'
        hash = get_id(source, [1, 5], {'z':-12.5})
        expected = self.manually_get_id(source, [1, 5], {'z':-12.5})
        self.assertEqual(hash, expected)

    def test_get_id_with_hash_xxhash(self):
        SpeeduPySettings().hash = ['xxhash']
        source = 'print("Essa é uma função de teste!")\nreturn x ** y / z'
        hash = get_id(source, [1, 5], {'z':-12.5})
        expected = self.manually_get_id(source, [1, 5], {'z':-12.5}, hash_algorithm=['xxhash'])
        self.assertEqual(hash, expected)

    def test_get_id_with_hash_murmur(self):
        SpeeduPySettings().hash = ['murmur']
        source = 'print("Essa é uma função de teste!")\nreturn x ** y / z'
        hash = get_id(source, [1, 5], {'z':-12.5})
        expected = self.manually_get_id(source, [1, 5], {'z':-12.5}, hash_algorithm=['murmur'])
        self.assertEqual(hash, expected)
        
    def test_get_id_without_fun_args(self):
        SpeeduPySettings().hash = ['xxhash']
        source = 'print("Testando!")\ninput("...")\nreturn x + y / -z'
        hash = get_id(source, fun_kwargs={'z':-12.5})
        expected = self.manually_get_id(source, [], {'z':-12.5}, hash_algorithm=['xxhash'])
        self.assertEqual(hash, expected)

    def test_get_id_without_fun_kwargs(self):
        SpeeduPySettings().hash = ['md5']
        source = 'print("Testando!")\nos.path.exists("/")\nrandom.randint()\nreturn x + y / -z'
        hash = get_id(source, fun_args=[-1.227, 0])
        expected = self.manually_get_id(source, [-1.227, 0], {})
        self.assertEqual(hash, expected)

    def test_get_id_only_with_fun_source(self):
        SpeeduPySettings().hash = ['murmur']
        source = 'print("Testando!")\nreturn x / y ** 2'
        hash = get_id(source)
        expected = self.manually_get_id(source, [], {}, hash_algorithm=['murmur'])
        self.assertEqual(hash, expected)

    def test_add_to_metadata(self):
        self.assertDictEqual(self.dataAccess._DataAccess__METADATA, {})

        hash = "hash_func_1"
        args = [1, True]
        kwargs = {'a':10, 'b': 'teste', 'c':[1, -2, 3.26]}
        f_call_hash_1 = self.manually_get_id(hash, args, kwargs)
        md1 = Metadata(hash, args, kwargs, 10, 2.12123)
        self.dataAccess.add_to_metadata(f_call_hash_1, md1)
        self.assertDictEqual(self.dataAccess._DataAccess__METADATA, {f_call_hash_1:[md1]})

        md2 = Metadata(hash, args, kwargs, 2, 4.112312)
        self.dataAccess.add_to_metadata(f_call_hash_1, md2)
        self.assertDictEqual(self.dataAccess._DataAccess__METADATA, {f_call_hash_1:[md1, md2]})

        hash = 'hash_func_2'
        args = []
        kwargs = {'a':-3, 'c':{1, -2, 3.26}}
        f_call_hash_2 = self.manually_get_id(hash, args, kwargs)
        md3 = Metadata(hash, args, kwargs, True, 4.12312312)
        self.dataAccess.add_to_metadata(f_call_hash_2, md3)
        self.assertDictEqual(self.dataAccess._DataAccess__METADATA, {f_call_hash_1:[md1, md2],
                                                                     f_call_hash_2:[md3]})

if __name__ == '__main__':
    unittest.main()