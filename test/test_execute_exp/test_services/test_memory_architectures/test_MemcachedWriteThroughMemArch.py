import unittest
from typing import Dict

from pymemcache.client.base import Client
from pymemcache.serde import pickle_serde

from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.services.memory_architecures.MemcachedWriteThroughMemArch import (
    MemcachedWriteThroughMemArch,
)
from test_execute_exp.test_services.test_memory_architectures.AbstractMemArchTest import (
    AbstractMemArchTest,
)


class TestMemcachedWriteThroughMemArch(AbstractMemArchTest, unittest.TestCase):
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
        return MemcachedWriteThroughMemArch(self.retrieval_strategy, False)

    def assert_cache_on_RAM_equal(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        if len(non_persisted_data) > 0:
            raise Exception(
                "Memcached write-through strategy does not allow non persisted data on RAM!"
            )

        self.wait_for_memcached_persistency()
        for k, v in persisted_data.items():
            self.assertEqual(self.memcached.get(k), v)

    def insert_data_on_cache_RAM(
        self,
        non_persisted_data: Dict[str, CacheData],
        persisted_data: Dict[str, CacheData],
    ) -> None:
        if len(non_persisted_data) > 0:
            raise Exception(
                "Memcached write-through strategy does not allow non persisted data on RAM!"
            )

        self.memcached.set_many(persisted_data, noreply=False)

    def wait_for_memcached_persistency(self):
        # Memcached answers the commands of one connection in order, so the reply
        # to a round trip on the arch's own client says its earlier writes (sent
        # with noreply) were applied. The sleep this replaces was a guess.
        self.mem_arch._memcached.client.version()

    def test_create_cache_entry_writes_through(self):
        self.mem_arch.create_cache_entry("hash123", "result")
        self.wait_for_memcached_persistency()

        self.assertEqual(self.memcached.get("hash123"), CacheData("hash123", "result"))
        self.retrieval_strategy.save_cache_data.assert_called_once()

    def test_save_new_cache_entries_does_nothing(self):
        self.mem_arch.save_new_cache_entries()
        self.retrieval_strategy.save_cache_data.assert_not_called()

    def test_get_new_cache_entries_size(self):
        size = self.mem_arch.get_new_cache_entries_size()
        self.assertEqual(size, 0)
