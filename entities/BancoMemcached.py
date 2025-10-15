import pickle
from pymemcache.client.base import Client
from SingletonMeta import SingletonMeta


def pickle_serializer(key, value):
    """Serializa o valor com pickle, retornando (bytes, flags)."""
    try:
        return pickle.dumps(value), 1  # flag 1 = dado serializado com pickle
    except Exception as e:
        # Se não for serializável, converte pra string e manda como bytes
        return str(value).encode("utf-8"),


def pickle_deserializer(key, value, flags):
    """Desserializa o valor conforme a flag."""
    if flags == 1:
        return pickle.loads(value)
    return value


class BancoMemcached(metaclass=SingletonMeta):
    def __init__(self):
        self.client = Client(
            ('127.0.0.1', 11211),
            serializer=pickle_serializer,
            deserializer=pickle_deserializer
        )

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value):
        self.client.set(key, value)

    def close_connection(self):
        self.client.close()
