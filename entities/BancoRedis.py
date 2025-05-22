import redis
from typing import Dict, List
from speedupy.SingletonMeta import SingletonMeta


# XXX: IMPLEMENTAR + TESTAR!!!!
class BancoRedis(metaclass=SingletonMeta):
	def __init__(self):
		self.client = redis.Redis(host='localhost', port=6379, db=0)

	def flush_database(self):
		self.client.flushdb()

	def dbsize(self):
		return self.client.dbsize()

	def get(self, key: str) -> bytes:
		return self.client.get(key).decode()

	def hget(self, h_key: str, f_key: str) -> bytes:
		return self.client.hget(h_key, f_key).decode()

	def get_all_key_value_pairs_inside_hash(self, h_key: str) -> Dict[str, bytes]:
		return {k.decode(): v.decode() for k, v in self.client.hgetall(h_key).items()}

	def get_all_key_value_pairs(self) -> Dict[str, bytes]:
		return {key.decode(): self.client.get(key).decode() for key in self.client.scan_iter()}

	def set(self, key: str, value: bytes):
		self.client.set(key, value)

	def set_group_of_key_value_pairs(self, data: Dict[str, bytes]):
		pipe = self.client.pipeline()
		for key, value in data.items(): pipe.set(key, value)
		pipe.execute()

	def set_group_of_hashes(self, data: Dict[str, List[str, bytes]]):
		pipe = self.client.pipeline()
		for h_key, value in data.items(): pipe.hset(h_key, mapping=value)
		pipe.execute()

	def close_connection(self):
		self.client.close()
