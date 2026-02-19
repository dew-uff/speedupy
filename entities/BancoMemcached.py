import atexit
from typing import Dict
from pymemcache.client.base import PooledClient
from pymemcache.serde import pickle_serde
from SingletonMeta import SingletonMeta

class BancoMemcached(metaclass=SingletonMeta):
    def __init__(self):
        self.client = PooledClient(('127.0.0.1', 11211),
                             serializer=pickle_serde.serialize,
                             deserializer=pickle_serde.deserialize,
                             max_pool_size=2)
        atexit.register(self.close_connection)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value):
        self.client.set(key, value)

    def set_group_of_key_value_pairs(self, data: Dict[str, bytes]):
        self.client.set_many(data)

    def close_connection(self):
        self.client.close()
