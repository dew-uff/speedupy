from typing import Optional
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from entities.BancoMemcached import BancoMemcached


class MemcachedWriteBackMemArch(AbstractMemArch):
    def __init__(self, retrieval_strategy, use_threads: bool):
        super().__init__(retrieval_strategy, use_threads)
        self.memcached = BancoMemcached()
        # Buffer local de novos dados ainda não persistidos
        self._NEW_DATA_DICTIONARY = {}

    def get_cache_entry(self, func_call_hash: str, func_name=None):
        # 1️ Tenta pegar do memcached
        cached_value = self.memcached.get(func_call_hash)
        if cached_value:
            return cached_value.output

        # 2️ Se não achou no cache, busca no storage
        persistent_cache_data = self._retrieval_strategy.get_cache_entry(func_call_hash, func_name)

        # 3️ Se achou no storage, armazena no memcached e devolve
        if persistent_cache_data:
            self.memcached.set(func_call_hash, persistent_cache_data)
            return persistent_cache_data.output

        return None

    def create_cache_entry(self, func_call_hash: str, func_return, func_name=None) -> None:
        # Cria o objeto CacheData normalmente
        cache_data = CacheData(func_call_hash, func_return, func_name)

        # 1️ Salva no memcached (rápido)
        self.memcached.set(func_call_hash, cache_data)

        # 2️ Guarda localmente (para persistir depois)
        self._NEW_DATA_DICTIONARY[func_call_hash] = cache_data

        #  Não salva ainda no banco

    def save_new_cache_entries(self) -> None:
        # 3️ No final, salva tudo de uma vez no storage persistente
        if self._NEW_DATA_DICTIONARY:
            self._retrieval_strategy.save_cache_data(self._NEW_DATA_DICTIONARY)
            # Limpa o buffer após persistir
            self._NEW_DATA_DICTIONARY.clear()
