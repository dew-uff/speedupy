import random
import unittest
from typing import Dict

from pymemcache.client.base import Client
from pymemcache.serde import pickle_serde
from test_helpers import random_str

from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.services.memory_architecures.MemcachedWriteBackMemArch import (
    MemcachedWriteBackMemArch,
)
from test_execute_exp.test_services.test_memory_architectures.AbstractMemArchTest import (
    AbstractMemArchTest,
)


class TestMemcachedWriteBackMemArch(AbstractMemArchTest, unittest.TestCase):
    def tearDown(self):
        super().tearDown()
        self.memcached.close()

    def create_instance(self) -> AbstractMemArch:
        self.memcached = Client(
            ("localhost", 11211),
            serializer=pickle_serde.serialize,
            deserializer=pickle_serde.deserialize,
        )
        self.memcached.flush_all(noreply=False)
        return MemcachedWriteBackMemArch(self.retrieval_strategy, False)

    def wait_for_memcached_persistency(self):
        # Memcached answers the commands of one connection in order, so the reply
        # to a round trip on the arch's own client says its earlier writes (sent
        # with noreply) were applied. The sleep this replaces was a guess.
        self.mem_arch._memcached.client.version()

    def assert_cache_on_RAM_equal(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        self.wait_for_memcached_persistency()
        cache_data = non_persisted_data | persisted_data
        for k, v in cache_data.items():
            self.assertEqual(self.memcached.get(k), v)

    def insert_data_on_cache_RAM(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        self.memcached.set_many(non_persisted_data, noreply=False)
        self.memcached.set_many(persisted_data, noreply=False)
        self.mem_arch._new_cache_keys += list(non_persisted_data.keys())

    def test_create_cache_entry(self):
        persisted_data = {
            "fc_hash2": CacheData("fc_hash2", {1, 2, 3}),
            "fc_hash3": CacheData("fc_hash3", False),
        }
        self.insert_data_on_cache_RAM({}, persisted_data)

        fc_hash = random_str()
        func_return = random.choices([10, True, {2, 3}, (5,), {"k": 10}])
        func_name = random.choice([random_str(), None])
        self.mem_arch.create_cache_entry(fc_hash, func_return, func_name=func_name)

        non_persisted_data = {fc_hash: CacheData(fc_hash, func_return, func_name)}
        self.assert_cache_on_RAM_equal(non_persisted_data, persisted_data)

    def test_save_new_cache_entries(self):
        fc_hash = random_str()
        func_return = random.choices([10, True, {2, 3}, (5,), {"k": 10}])
        func_name = random.choice([random_str(), None])
        non_persisted_data = {fc_hash: CacheData(fc_hash, func_return, func_name)}
        self.insert_data_on_cache_RAM(non_persisted_data, {})

        self.mem_arch.save_new_cache_entries()

        self.retrieval_strategy.save_cache_data.assert_called_once_with(
            non_persisted_data
        )

    def test_create_cache_entry_writes_only_to_memcached(self):
        self.mem_arch.create_cache_entry("hash123", "resultado")

        self.wait_for_memcached_persistency()
        self.assertEqual(
            self.memcached.get("hash123"), CacheData("hash123", "resultado")
        )
        self.retrieval_strategy.save_cache_data.assert_not_called()
        self.assertListEqual(self.mem_arch._new_cache_keys, ["hash123"])

    def test_save_new_cache_entries_persists_dirty_data(self):
        non_persisted_data = {"hash123": CacheData("hash123", "resultado")}
        self.insert_data_on_cache_RAM(non_persisted_data, {})

        self.mem_arch.save_new_cache_entries()

        self.retrieval_strategy.save_cache_data.assert_called_once_with(
            non_persisted_data
        )

    def test_get_new_cache_entries_size(self):
        persisted_data = {"func_call_hash": CacheData("func_call_hash", "test", "f")}
        non_persisted_data, expected_size = random.choice(
            [
                [{}, 5],
                [{"fc_hash": CacheData("fc_hash", 10, "func")}, 196],
                [{"fc_hash2": CacheData("fc_hash2", False, None)}, 191],
            ]
        )
        self.insert_data_on_cache_RAM(non_persisted_data, persisted_data)

        size = self.mem_arch.get_new_cache_entries_size()

        self.assertEqual(size, expected_size)
