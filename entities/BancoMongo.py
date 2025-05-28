import atexit
from pymongo import MongoClient, UpdateOne
from typing import Optional, Dict
from SingletonMeta import SingletonMeta


class BancoMongo(metaclass=SingletonMeta):
	DB_NAME = 'speedupy'
	COLLECTION_NAME = 'CACHE'

	@classmethod
	def database_exists(cls) -> bool:
		return cls.DB_NAME in BancoMongo().client.list_database_names()

	def __init__(self):
		self.client = MongoClient("mongodb://localhost:27017/")
		self.cache = self.client[self.DB_NAME][self.COLLECTION_NAME]
		atexit.register(self.cleanup)

	def flush_database(self) -> None:
		self.client.drop_database(self.DB_NAME)

	def get_all_key_value_pairs(self) -> Dict[str, bytes]:
		return {doc['_id']: doc['value'] for doc in self.cache.find()}

	def get_document_data(self, doc_id: str) -> Dict[str, bytes]:
		doc = self.cache.find_one({"_id": doc_id})
		if doc is None: return {}
		return {k: v for k, v in doc.items() if k != '_id'}

	def get_document_field(self, doc_id: str, key='value') -> Optional[bytes]:
		try: return self.cache.find_one({"_id": doc_id})[key]
		except (TypeError, KeyError): return

	def set_group_of_key_value_pairs(self, data: Dict[str, bytes]) -> None:
		operations = [UpdateOne({"_id": k}, {"$set": {'value': v}}, upsert=True) for k, v in data.items()]
		self.cache.bulk_write(operations)

	def set_group_of_hashes(self, data: Dict[str, Dict[str, bytes]]) -> None:
		operations = [UpdateOne({"_id": h_key}, {"$set": value}, upsert=True) for h_key, value in data.items()]
		self.cache.bulk_write(operations)

	def cleanup(self):
		self.client.close()
