import pickle
from pymemcache.client.base import Client
from pymemcache.serde import pickle_serde
from SingletonMeta import SingletonMeta

class BancoMemcached(metaclass=SingletonMeta):
    def __init__(self):
        self.client = Client(('127.0.0.1', 11211),
                             serializer=pickle_serde.serialize,
                             deserializer=pickle_serde.deserialize)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value):
        self.client.set(key, value)

    def close_connection(self):
        self.client.close()
