from typing import Optional
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from entities.BancoMemcached import BancoMemcached


class MemcachedWriteThroughMemArch(AbstractMemArch):
    def __init__(self, retrieval_strategy, use_threads: bool):
        super().__init__(retrieval_strategy, use_threads)
        self.memcached = BancoMemcached()

    def get_cache_entry(self, func_call_hash: str, func_name=None):
        # 1️ Tenta buscar no memcached
        cached_value = self.memcached.get(func_call_hash)
        if cached_value:
            return cached_value.output

        # 2️ Se não achou, busca no armazenamento persistente (ex: MySQL)
        persistent_cache_data = self._retrieval_strategy.get_cache_entry(func_call_hash, func_name)

        # 3️ Se achou, salva no memcached pra próxima vez
        if persistent_cache_data:
            self.memcached.set(func_call_hash, persistent_cache_data)
            return persistent_cache_data.output

        return None

    def create_cache_entry(self, func_call_hash: str, func_return, func_name=None) -> None:
        # Cria o objeto de cache
        cache_data = CacheData(func_call_hash, func_return, func_name)

        # Escreve tanto no memcached quanto no storage persistente
        self.memcached.set(func_call_hash, cache_data)
        self._retrieval_strategy.save_cache_data({func_call_hash: cache_data})

    def save_new_cache_entries(self) -> None:
        # Não precisa fazer nada, pois o write-through já foi feito
        pass
