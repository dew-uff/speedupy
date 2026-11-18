import atexit
from typing import Dict, Optional

try:
    from gridfs import GridFSBucket
    from pymongo import MongoClient
except ImportError as error:
    raise ImportError(
        "The mongo backend needs the pymongo driver, which is not installed; "
        'install it with: pip install "speedupy[mongo]"'
    ) from error

from SingletonMeta import SingletonMeta


class BancoGridFS(metaclass=SingletonMeta):
    DB_NAME = "speedupy"
    BUCKET_NAME = "CACHE_GRIDFS"

    @classmethod
    def database_exists(cls) -> bool:
        return cls.DB_NAME in BancoGridFS().client.list_database_names()

    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[self.DB_NAME]
        self.fs = GridFSBucket(self.db, bucket_name=self.BUCKET_NAME)
        atexit.register(self.cleanup)

    def flush_database(self) -> None:
        self.client.drop_database(self.DB_NAME)

    def get_all_key_value_pairs(self) -> Dict[str, bytes]:
        return {grid_out.filename: grid_out.read() for grid_out in self.fs.find()}

    def get_documents_by_metadata(self, metadata: Dict[str, str]) -> Dict[str, bytes]:
        return {
            grid_out.filename: grid_out.read() for grid_out in self.fs.find(metadata)
        }

    def get_document_by_filename(self, filename: str) -> Optional[bytes]:
        try:
            grid_out = self.fs.find({"filename": filename}).next()
            return grid_out.read()
        except StopIteration:
            return None

    def set_group_of_key_value_pairs(self, data: Dict[str, bytes]) -> None:
        for filename, value in data.items():
            self._replace(filename, value)

    def set_group_of_hashes(self, data: Dict[str, Dict[str, bytes]]) -> None:
        for func_name, hashes in data.items():
            for func_call_hash, value in hashes.items():
                self._replace(func_call_hash, value, metadata={"func_name": func_name})

    def _replace(
        self, filename: str, value: bytes, metadata: Optional[Dict] = None
    ) -> None:
        for grid_out in self.fs.find({"filename": filename}):
            self.fs.delete(grid_out._id)
        self.fs.upload_from_stream(filename, value, metadata=metadata or {})

    def cleanup(self):
        self.client.close()
