import pickle
from typing import Dict, Optional

from execute_exp.services.storages.Storage import Storage
from execute_exp.entitites.CacheData import CacheData
from entities.BancoRedis import BancoRedis


# XXX: IMPLEMENTAR E TESTAR!
class RedisStorage(Storage):
    def __init__(self):
        self.redis = BancoRedis()

    # XXX: TALVEZ SEJA POSSÍVEL JÁ SALVAR NO REDIS OS DADOS NESSA ESTRUTURA
    def get_all_cached_data(self, use_isolated_connection=False) -> Dict[str, CacheData]:
        return {func_call_hash: CacheData(func_call_hash, pickle.loads(func_output))
                for func_call_hash, func_output in self.redis.get_all_key_value_pairs()}

    # XXX: TALVEZ SEJA POSSÍVEL JÁ SALVAR NO REDIS OS DADOS NESSA ESTRUTURA
    def get_cached_data_of_a_function(self, func_name: str, use_isolated_connection=False) -> Dict[str, CacheData]:
        results = self.redis.get_all_key_value_pairs_inside_hash(func_name)
        return {func_call_hash: CacheData(func_call_hash, pickle.loads(func_output), func_name=func_name)
                for func_call_hash, func_output in results}

    # XXX: NECESSÁRIO PASSAR O HASH DA FUNÇÃO CASO A ESTRATÉGIA DE RECUPERAÇÃO SEJA FUNCTION
    def get_cached_data_of_a_function_call(self, func_call_hash: str, func_name=None, use_isolated_connection=False) -> Optional[CacheData]:
        try:
            result = self.redis.hget(func_name, func_call_hash) if func_name else self.redis.get(func_call_hash)
            func_output = pickle.loads(result)
            return CacheData(func_call_hash, func_output)
        except TypeError: pass

    def save_cache_data(self, data: Dict[str, CacheData], use_isolated_connection=False) -> None:
        if len(data) == 0: return

        records = {}
        v = list(data.values())[0]
        if v.func_name:
            for func_call_hash, cache_data in data.items(): records[cache_data.func_name][func_call_hash] = pickle.dumps(cache_data.output)
            self.redis.set_group_of_hashes(records)
        else:
            for func_call_hash, cache_data in data.items(): records[func_call_hash] = pickle.dumps(cache_data.output)
            self.redis.set_group_of_key_value_pairs(records)

    def __del__(self):
        self.redis.fechar_conexao()
