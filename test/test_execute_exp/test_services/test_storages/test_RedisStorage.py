import redis, unittest, os, sys
from typing import Dict

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.storages.RedisStorage import RedisStorage
from execute_exp.services.storages.Storage import Storage
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.entitites.CacheData import CacheData
from test_execute_exp.test_services.test_storages.AbstractStorageTest import AbstractStorageTest


class TestRedisStorage(AbstractStorageTest, unittest.TestCase):
    def setUp(self):
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            r.close()
        except:
            self.skipTest("Redis is not running. Skipping RedisStorage tests.")
        super().setUp()

    def create_instance(self, serializer: Serializer) -> Storage:
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.redis.flushdb()

        return RedisStorage(serializer)

    def assert_storage_is_empty(self):
        self.assertEqual(self.redis.dbsize(), 0)

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        if len(expected_data) == 0 and self.redis.dbsize() == 0: return

        key = self.redis.randomkey()
        if not key: return 

        if self.redis.type(key) == b'hash':
            data_gotten = {func_call_hash.decode(): CacheData(func_call_hash.decode(), self.serializer.loads(func_output), func_name.decode())
                           for func_name in self.redis.scan_iter()
                           for func_call_hash, func_output in self.redis.hgetall(func_name).items()}
        else:
            data_gotten = {key.decode(): CacheData(key.decode(), self.serializer.loads(self.redis.get(key))) for key in self.redis.scan_iter()}
        self.assert_data_gotten_is_correct(data_gotten, expected_data)

    def manually_cache_a_record(self, func_hash, func_return, func_name=None, **kwargs):
        if func_name: self.redis.hset(func_name, func_hash, self.serializer.dumps(func_return))
        else: self.redis.set(func_hash, self.serializer.dumps(func_return))

    def __del__(self):
        if hasattr(self, 'redis'):
            self.redis.close()