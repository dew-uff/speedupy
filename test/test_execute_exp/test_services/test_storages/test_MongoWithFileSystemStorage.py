import os
import random
import unittest
from typing import Dict

import pymongo

from constants import Constants
from entities.MongoDatabase import MongoDatabase
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.FileSystemStorage import FileSystemStorage
from execute_exp.services.storages.MongoStorage import MongoStorage
from execute_exp.services.storages.MongoWithFileSystemStorage import (
    MongoWithFileSystemStorage,
)
from execute_exp.services.storages.Storage import Storage
from test_execute_exp.test_services.test_storages.AbstractStorageTest import (
    AbstractStorageTest,
)


class TestMongoWithFileSytemStorage(AbstractStorageTest, unittest.TestCase):
    def create_instance(self, serializer: Serializer) -> Storage:
        self.mongo = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mongo_cache = self.mongo[MongoDatabase.DB_NAME][
            MongoDatabase.COLLECTION_NAME
        ]
        self.mongo.drop_database(MongoDatabase.DB_NAME)
        mongo_storage = MongoStorage(serializer)

        os.makedirs(Constants().CACHE_FOLDER_NAME)
        filesystem_storage = FileSystemStorage(serializer)
        filesystem_storage.CACHE_FOLDER_NAME = Constants().CACHE_FOLDER_NAME

        return MongoWithFileSystemStorage(mongo_storage, filesystem_storage)

    def assert_storage_is_empty(self):
        self.assertEqual(self.mongo_cache.count_documents({}), 0)
        self.assertListEqual(os.listdir(Constants().CACHE_FOLDER_NAME), [])

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        data_gotten = {}
        fs_content = os.listdir(Constants().CACHE_FOLDER_NAME)

        if (
            len(expected_data) == 0
            and self.mongo_cache.count_documents({}) == 0
            and len(fs_content) == 0
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

        if len(fs_content) > 0:
            if os.path.isdir(
                os.path.join(Constants().CACHE_FOLDER_NAME, fs_content[0])
            ):
                for folder in fs_content:
                    files = os.listdir(
                        os.path.join(Constants().CACHE_FOLDER_NAME, folder)
                    )
                    for filename in files:
                        file_path = os.path.join(
                            Constants().CACHE_FOLDER_NAME, folder, filename
                        )
                        with open(file_path, "rb") as f:
                            output = self.serializer.load(f)
                        data_gotten[filename] = CacheData(filename, output, folder)
            else:
                for filename in fs_content:
                    file_path = os.path.join(Constants().CACHE_FOLDER_NAME, filename)
                    with open(file_path, "rb") as f:
                        output = self.serializer.load(f)
                    data_gotten[filename] = CacheData(filename, output)

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
            folder_path = Constants().CACHE_FOLDER_NAME
            if func_name:
                folder_path = os.path.join(folder_path, func_name)
                os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, func_hash)
            with open(file_path, "wb") as f:
                self.serializer.dump(func_return, f)

    def test_get_all_cached_data_when_cache_records_are_on_both_storages(self):
        # Create a payload slightly larger than 16MB
        big_str = "x" * (16 * 1024 * 1024 + 1024)  # 16MB + 1KB
        self.manually_cache_a_record("func_call_hash1", (big_str,))

        self.manually_cache_a_record("func_call_hash2", (True, 2, 5))
        self.manually_cache_a_record("func_call_hash3", [{"key1": 10, "key_2": False}])

        cached_data = self.storage.get_all_cached_data()

        expected_data = {
            "func_call_hash1": CacheData("func_call_hash1", (big_str,)),
            "func_call_hash2": CacheData("func_call_hash2", (True, 2, 5)),
            "func_call_hash3": CacheData(
                "func_call_hash3", [{"key1": 10, "key_2": False}]
            ),
        }
        self.assert_data_gotten_is_correct(cached_data, expected_data)

    def test_get_cached_data_of_a_function_when_cache_records_are_on_both_storages(
        self,
    ):
        # Create a payload slightly larger than 16MB
        big_str = "x" * (16 * 1024 * 1024 + 1024)  # 16MB + 1KB
        self.manually_cache_a_record("func_call_hash1", (big_str,), func_name="f1")

        self.manually_cache_a_record("func_call_hash2", (1,), func_name="f1")
        self.manually_cache_a_record("func_call_hash3", [10, -4, False], func_name="f1")

        cached_data = self.storage.get_cached_data_of_a_function("f1")

        expected_data = {
            "func_call_hash1": CacheData("func_call_hash1", (big_str,), func_name="f1"),
            "func_call_hash2": CacheData("func_call_hash2", (1,), func_name="f1"),
            "func_call_hash3": CacheData(
                "func_call_hash3", [10, -4, False], func_name="f1"
            ),
        }
        self.assert_data_gotten_is_correct(cached_data, expected_data)

    def test_get_cached_data_of_a_function_call_when_cache_record_exists_on_filesystem_storage(
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

        cache_data = self.storage.get_cached_data_of_a_function_call(
            "func_call_hash1", func_name=func_name
        )
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
