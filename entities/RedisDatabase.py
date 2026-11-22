import atexit
from typing import Dict

try:
    import redis
except ImportError as error:
    raise ImportError(
        "The redis backend needs the redis driver, which is not installed; "
        'install it with: pip install "speedupy[redis]"'
    ) from error

from entities.server_errors import server_unreachable
from SingletonMeta import SingletonMeta


class RedisDatabase(metaclass=SingletonMeta):
    MAX_PIPELINE_SIZE_MB = 1024

    def __init__(self):
        self.client = redis.Redis(
            host="localhost", port=6379, db=0, socket_connect_timeout=2
        )
        # Probe once, here, so a missing server fails with a clear message
        # before any cache operation. The read and write paths are untouched.
        try:
            self.client.ping()
        except redis.exceptions.RedisError as error:
            raise server_unreachable(
                "redis",
                "Redis",
                "localhost:6379",
                "https://redis.io/docs/latest/operate/oss_and_stack/install/",
                "redis",
            ) from error
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
            size_mb += (len(key.encode("utf-8")) + len(value)) / (1024 * 1024)
            if size_mb > self.MAX_PIPELINE_SIZE_MB - 1:
                pipe.execute()
                pipe = self.client.pipeline()
                size_mb = 0
        pipe.execute()

    def set_group_of_hashes(self, data: Dict[str, Dict[str, bytes]]):
        pipe = self.client.pipeline()
        for h_key, value in data.items():
            pipe.hset(h_key, mapping=value)
        pipe.execute()

    def cleanup(self):
        self.client.close()
