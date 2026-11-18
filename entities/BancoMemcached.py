import atexit
from typing import Dict

try:
    from pymemcache.client.base import Client
    from pymemcache.serde import pickle_serde
except ImportError as error:
    raise ImportError(
        "The memcached backend needs the pymemcache driver, which is not installed; "
        'install it with: pip install "speedupy[memcached]"'
    ) from error

from SingletonMeta import SingletonMeta


class BancoMemcached(metaclass=SingletonMeta):
    def __init__(self):
        self.client = Client(
            ("localhost", 11211),
            serializer=pickle_serde.serialize,
            deserializer=pickle_serde.deserialize,
        )
        atexit.register(self.close_connection)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value):
        self.client.set(key, value)

    def set_group_of_key_value_pairs(self, data: Dict[str, bytes]):
        self.client.set_many(data)

    def flush_cache(self):
        self.client.flush_all()

    def close_connection(self):
        self.client.close()
