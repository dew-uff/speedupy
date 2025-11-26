import pymongo, unittest, os, sys
from typing import Dict

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from entities.BancoMongo import BancoMongo
from execute_exp.services.storages.MongoStorage import MongoStorage
from execute_exp.services.storages.Storage import Storage
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.entitites.CacheData import CacheData
from test_execute_exp.test_services.test_storages.AbstractStorageTest import AbstractStorageTest


class TestMongoStorage(AbstractStorageTest, unittest.TestCase):
    def setUp(self):
        client = None
        try:
            client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=1000)
            client.server_info()
        except:
            if client: client.close()
            self.skipTest("MongoDB not available (Skipping MongoStorage tests)")
        
        if client: client.close()
        
        super().setUp()

    def create_instance(self, serializer: Serializer) -> Storage:
        self.mongo = pymongo.MongoClient("mongodb://localhost:27017/")
        self.cache = self.mongo[BancoMongo.DB_NAME][BancoMongo.COLLECTION_NAME]
        self.mongo.drop_database(BancoMongo.DB_NAME)

        return MongoStorage(serializer)

    def assert_storage_is_empty(self):
        self.assertEqual(self.cache.count_documents({}), 0)

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        if len(expected_data) == 0 and self.cache.count_documents({}) == 0: return

        doc = self.cache.find_one()
        if not doc:
            self.assert_data_gotten_is_correct({}, expected_data)
            return

        if 'value' not in doc:
            data_gotten = {func_call_hash: CacheData(func_call_hash, self.serializer.loads(func_output), func_name=doc['_id'])
                           for doc in self.cache.find()
                           for func_call_hash, func_output in doc.items() if func_call_hash != '_id'}
        else:
            data_gotten = {doc['_id']: CacheData(doc['_id'], self.serializer.loads(doc['value'])) for doc in self.cache.find()}
        self.assert_data_gotten_is_correct(data_gotten, expected_data)

    def manually_cache_a_record(self, func_hash, func_return, func_name=None, **kwargs):
        if func_name: self.cache.update_one({"_id": func_name}, {"$set": {func_hash: self.serializer.dumps(func_return)}}, upsert=True)
        else: self.cache.insert_one({'_id': func_hash, 'value': self.serializer.dumps(func_return)})

    def __del__(self):
        if hasattr(self, 'mongo'):
            self.mongo.close()