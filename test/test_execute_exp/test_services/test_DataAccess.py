import unittest, os, sys, hashlib, mmh3, xxhash, random
from unittest.mock import Mock

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.DataAccess import DataAccess
from execute_exp.SpeeduPySettings import SpeeduPySettings
from execute_exp.services.serializers.PickleSerializer import PickleSerializer
from execute_exp.services.serializers.CloudpickleSerializer import CloudpickleSerializer
from execute_exp.entitites.Metadata import Metadata


class TestDataAccess(unittest.TestCase):
    def setUp(self):
        serializer = random.choice([['pickle', PickleSerializer()],
                                    ['cloudpickle', CloudpickleSerializer()]])
        SpeeduPySettings().serializer = [serializer[0]]
        SpeeduPySettings().hash = [random.choice(['md5', 'murmur', 'xxhash'])]
        self.serializer = serializer[1]
        self.dataAccess = DataAccess()
        self.dataAccess._FUNCTIONS_2_HASHES = {'f1': 'f1_hash',
                                               'f2': 'f2_hash',
                                               'f3': 'f3_hash'}
        self.dataAccess._hash = Mock()

    def tearDown(self) -> None:
        self.dataAccess._DataAccess__METADATA = {}

    def manually_get_id(self, f_source, f_args, f_kwargs, hash_algorithm=['md5']):
        f_call_hash = b''
        if f_args != []: f_call_hash += self.serializer.dumps(f_args)
        if f_kwargs != {}: f_call_hash += self.serializer.dumps(f_kwargs)
        f_call_hash = str(f_call_hash) + f_source
        if hash_algorithm == ['md5']:
            f_call_hash = hashlib.md5(f_call_hash.encode('utf')).hexdigest()
        elif hash_algorithm == ['murmur']:
            f_call_hash = hex(mmh3.hash128(f_call_hash.encode('utf')))[2:]
        elif hash_algorithm == ['xxhash']:
            f_call_hash = xxhash.xxh128_hexdigest(f_call_hash.encode('utf'))
        return f_call_hash

    def test_get_function_hash(self):
        func = random.choice(list(self.dataAccess._FUNCTIONS_2_HASHES.keys()))
        func_hash = self.dataAccess.get_function_hash(func)
        self.assertEqual(func_hash, self.dataAccess._FUNCTIONS_2_HASHES[func])

    def test_get_id(self):
        self.dataAccess._hash.get_id = Mock(return_value='fc_hash')

        func = random.choice(list(self.dataAccess._FUNCTIONS_2_HASHES.keys()))
        args = (1,)
        kwargs = {'a': True}
        id = self.dataAccess.get_id(func, args, kwargs)

        self.dataAccess._hash.get_id.assert_called_once_with(self.dataAccess._FUNCTIONS_2_HASHES[func], args, kwargs)
        self.assertEqual(id, 'fc_hash')

    def test_add_to_metadata(self):
        self.assertDictEqual(self.dataAccess._DataAccess__METADATA, {})

        hash = "hash_func_1"
        args = [1, True]
        kwargs = {'a': 10, 'b': 'teste', 'c': [1, -2, 3.26]}
        f_call_hash_1 = self.manually_get_id(hash, args, kwargs)
        md1 = Metadata(hash, args, kwargs, 10, 2.12123)
        self.dataAccess.add_to_metadata(f_call_hash_1, md1)
        self.assertDictEqual(self.dataAccess._DataAccess__METADATA, {f_call_hash_1: [md1]})

        md2 = Metadata(hash, args, kwargs, 2, 4.112312)
        self.dataAccess.add_to_metadata(f_call_hash_1, md2)
        self.assertDictEqual(self.dataAccess._DataAccess__METADATA, {f_call_hash_1: [md1, md2]})

        hash = 'hash_func_2'
        args = []
        kwargs = {'a': -3, 'c': {1, -2, 3.26}}
        f_call_hash_2 = self.manually_get_id(hash, args, kwargs)
        md3 = Metadata(hash, args, kwargs, True, 4.12312312)
        self.dataAccess.add_to_metadata(f_call_hash_2, md3)
        self.assertDictEqual(self.dataAccess._DataAccess__METADATA, {f_call_hash_1: [md1, md2],
                                                                     f_call_hash_2: [md3]})


if __name__ == '__main__':
    unittest.main()
