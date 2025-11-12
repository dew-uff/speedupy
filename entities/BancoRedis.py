import atexit, redis
from typing import Dict
from SingletonMeta import SingletonMeta


class BancoRedis(metaclass=SingletonMeta):
	MAX_PIPELINE_SIZE_MB = 1024

	def __init__(self):
		self.client = redis.Redis(host='localhost', port=6379, db=0)
		atexit.register(self.cleanup)

	def flush_database(self):
		self.client.flushdb()

	def dbsize(self):
		return self.client.dbsize()

	def get(self, key: str) -> bytes:
		return self.client.get(key)

	def hget(self, h_key: str, f_key: str) -> bytes:
		return self.client.hget(h_key, f_key)

	def get_all_key_value_pairs_inside_hash(self, h_key: str) -> Dict[str, bytes]:
		return {k.decode(): v for k, v in self.client.hgetall(h_key).items()}

	def get_all_key_value_pairs(self) -> Dict[str, bytes]:
		return {key.decode(): self.client.get(key) for key in self.client.scan_iter()}

	def set_group_of_key_value_pairs(self, data: Dict[str, bytes]):
		pipe = self.client.pipeline()
		size_mb = 0
		for key, value in data.items():
			pipe.set(key, value)
			size_mb += (len(key.encode('utf-8')) + len(value)) / (1024 * 1024)
			if size_mb > self.MAX_PIPELINE_SIZE_MB - 1:
				pipe.execute()
				pipe = self.client.pipeline()
				size_mb = 0
		pipe.execute()

	def set_group_of_hashes(self, data: Dict[str, Dict[str, bytes]]):
		pipe = self.client.pipeline()
		for h_key, value in data.items(): pipe.hset(h_key, mapping=value)
		pipe.execute()

	def cleanup(self):
		self.client.close()
