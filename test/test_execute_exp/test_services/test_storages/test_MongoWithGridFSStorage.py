import os
import random
import sys
import unittest
from typing import Dict

import gridfs
import pymongo

project_folder = os.path.realpath(__file__).split("test/")[0]
sys.path.append(project_folder)

from entities.BancoGridFS import BancoGridFS
from entities.BancoMongo import BancoMongo
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.GridFSStorage import GridFSStorage
from execute_exp.services.storages.MongoStorage import MongoStorage
from execute_exp.services.storages.MongoWithGridFSStorage import MongoWithGridFSStorage
from execute_exp.services.storages.Storage import Storage
from test_execute_exp.test_services.test_storages.AbstractStorageTest import (
    AbstractStorageTest,
)


class TestMongoWithGridFSStorage(AbstractStorageTest, unittest.TestCase):
    def create_instance(self, serializer: Serializer) -> Storage:
        self.mongo = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mongo_cache = self.mongo[BancoMongo.DB_NAME][BancoMongo.COLLECTION_NAME]
        self.mongo.drop_database(BancoMongo.DB_NAME)
        mongo_storage = MongoStorage(serializer)

        self.db = self.mongo[BancoGridFS.DB_NAME]
        self.fs = gridfs.GridFSBucket(self.db, bucket_name=BancoGridFS.BUCKET_NAME)
        gridfs_storage = GridFSStorage(serializer)

        return MongoWithGridFSStorage(mongo_storage, gridfs_storage)

    def assert_storage_is_empty(self):
        self.assertEqual(self.mongo_cache.count_documents({}), 0)
        self.assertEqual(
            self.db[f"{BancoGridFS.BUCKET_NAME}.files"].count_documents({}), 0
        )

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        data_gotten = {}
        grid_outs = list(self.fs.find())

        if (
            len(expected_data) == 0
            and self.mongo_cache.count_documents({}) == 0
            and len(grid_outs) == 0
        ):
            return

        doc = self.mongo_cache.find_one()
        if self.mongo_cache.count_documents({}) != 0:
            if "value" not in doc:
                # function retrieval strategy!
                data_gotten = {
                    func_call_hash: CacheData(
                        func_call_hash,
                        self.serializer.loads(func_output),
                        func_name=doc["_id"],
                    )
                    for doc in self.mongo_cache.find()
                    for func_call_hash, func_output in doc.items()
                    if func_call_hash != "_id"
                }
            else:
                data_gotten = {
                    doc["_id"]: CacheData(
                        doc["_id"], self.serializer.loads(doc["value"])
                    )
                    for doc in self.mongo_cache.find()
                }

        for grid_out in grid_outs:
            func_name = (
                grid_out.metadata.get("func_name") if grid_out.metadata else None
            )
            data_gotten[grid_out.filename] = CacheData(
                grid_out.filename,
                self.serializer.loads(grid_out.read()),
                func_name=func_name,
            )

        self.assert_data_gotten_is_correct(data_gotten, expected_data)

    def manually_cache_a_record(self, func_hash, func_return, func_name=None, **kwargs):
        try:
            if func_name:
                self.mongo_cache.update_one(
                    {"_id": func_name},
                    {"$set": {func_hash: self.serializer.dumps(func_return)}},
                    upsert=True,
                )
            else:
                self.mongo_cache.insert_one(
                    {"_id": func_hash, "value": self.serializer.dumps(func_return)}
                )
        except (pymongo.errors.DocumentTooLarge, pymongo.errors.OperationFailure):
            metadata = {"func_name": func_name} if func_name else {}
            self.fs.upload_from_stream(
                func_hash, self.serializer.dumps(func_return), metadata=metadata
            )

    def test_get_all_cached_data_when_cache_records_are_on_both_storages(self):
        # Create a payload slightly larger than 16MB
        big_str = "x" * (16 * 1024 * 1024 + 1024)  # 16MB + 1KB
        self.manually_cache_a_record("func_call_hash1", (big_str,))

        self.manually_cache_a_record("func_call_hash2", (True, 2, 5))
        self.manually_cache_a_record("func_call_hash3", [{"key1": 10, "key_2": False}])

        dicio = self.storage.get_all_cached_data()

        expected_data = {
            "func_call_hash1": CacheData("func_call_hash1", (big_str,)),
            "func_call_hash2": CacheData("func_call_hash2", (True, 2, 5)),
            "func_call_hash3": CacheData(
                "func_call_hash3", [{"key1": 10, "key_2": False}]
            ),
        }
        self.assert_data_gotten_is_correct(dicio, expected_data)

    def test_get_cached_data_of_a_function_when_cache_records_are_on_both_storages(
        self,
    ):
        # Create a payload slightly larger than 16MB
        big_str = "x" * (16 * 1024 * 1024 + 1024)  # 16MB + 1KB
        self.manually_cache_a_record("func_call_hash1", (big_str,), func_name="f1")

        self.manually_cache_a_record("func_call_hash2", (1,), func_name="f1")
        self.manually_cache_a_record("func_call_hash3", [10, -4, False], func_name="f1")

        dicio = self.storage.get_cached_data_of_a_function("f1")

        expected_data = {
            "func_call_hash1": CacheData("func_call_hash1", (big_str,), func_name="f1"),
            "func_call_hash2": CacheData("func_call_hash2", (1,), func_name="f1"),
            "func_call_hash3": CacheData(
                "func_call_hash3", [10, -4, False], func_name="f1"
            ),
        }
        self.assert_data_gotten_is_correct(dicio, expected_data)

    def test_get_cached_data_of_a_function_call_when_cache_record_exists_on_gridfs_storage(
        self,
    ):
        # Create a payload slightly larger than 16MB
        func_name = None
        if random.random() < 0.5:
            func_name = "f2"
        big_str = "x" * (16 * 1024 * 1024 + 1024)  # 16MB + 1KB
        self.manually_cache_a_record("func_call_hash1", (big_str,), func_name=func_name)

        self.manually_cache_a_record("func_call_hash2", [1, {2, 4, 1}, -2])
        self.manually_cache_a_record("func_call_hash3", "My test")

        cache_data = self.storage.get_cached_data_of_a_function_call("func_call_hash1")
        self.assert_two_cache_data_are_equal(
            cache_data, CacheData("func_call_hash1", (big_str,), func_name=func_name)
        )

    def test_save_cache_data_that_exceeds_mongo_document_limit(self):
        # Create a payload slightly larger than 16MB
        big_str = "x" * (16 * 1024 * 1024 + 1024)  # 16MB + 1KB

        func_name = None
        if random.random() < 0.5:
            func_name = "f2"

        data = {
            "func_call_hash2": CacheData(
                "func_call_hash2", (big_str,), func_name=func_name
            )
        }

        self.storage.save_cache_data(data)
        self.assert_cached_data(data)

    def __del__(self):
        self.mongo.close()
