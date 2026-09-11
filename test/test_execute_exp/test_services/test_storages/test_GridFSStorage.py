import pymongo, gridfs, unittest, os, sys
from typing import Dict

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from entities.BancoGridFS import BancoGridFS
from execute_exp.services.storages.GridFSStorage import GridFSStorage
from execute_exp.services.storages.Storage import Storage
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.entitites.CacheData import CacheData
from test_execute_exp.test_services.test_storages.AbstractStorageTest import AbstractStorageTest


class TestGridFSStorage(AbstractStorageTest, unittest.TestCase):
    def create_instance(self, serializer: Serializer) -> Storage:
        self.mongo = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo[BancoGridFS.DB_NAME]
        self.mongo.drop_database(BancoGridFS.DB_NAME)
        self.fs = gridfs.GridFSBucket(self.db, bucket_name=BancoGridFS.BUCKET_NAME)

        return GridFSStorage(serializer)

    def assert_storage_is_empty(self):
        self.assertEqual(self.db[f"{BancoGridFS.BUCKET_NAME}.files"].count_documents({}), 0)

    def assert_cached_data(self, expected_data: Dict[str, CacheData]):
        grid_outs = list(self.fs.find())
        if len(expected_data) == 0 and len(grid_outs) == 0: return

        data_gotten = {}
        for grid_out in grid_outs:
            func_name = grid_out.metadata.get('func_name') if grid_out.metadata else None
            data_gotten[grid_out.filename] = CacheData(grid_out.filename, self.serializer.loads(grid_out.read()), func_name=func_name)
        self.assert_data_gotten_is_correct(data_gotten, expected_data)

    def manually_cache_a_record(self, func_hash, func_return, func_name=None, **kwargs):
        metadata = {'func_name': func_name} if func_name else {}
        self.fs.upload_from_stream(func_hash, self.serializer.dumps(func_return), metadata=metadata)

    def __del__(self):
        self.mongo.close()
