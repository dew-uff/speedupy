from typing import Dict, Optional

from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.Storage import Storage
from execute_exp.entitites.CacheData import CacheData
from entities.BancoMongo import BancoMongo


class MongoWithFileSystemStorage(Storage):
    def __init__(self, serializer: Serializer):
        super().__init__(serializer)
        self.mongo = BancoMongo()

    def get_all_cached_data(self, use_isolated_connection=False) -> Dict[str, CacheData]:
        return {func_call_hash: CacheData(func_call_hash, self._serializer.loads(func_output))
                for func_call_hash, func_output in self.mongo.get_all_key_value_pairs().items()}

    def get_cached_data_of_a_function(self, func_name: str, use_isolated_connection=False) -> Dict[str, CacheData]:
        results = self.mongo.get_document_data(func_name).items()
        return {func_call_hash: CacheData(func_call_hash, self._serializer.loads(func_output), func_name=func_name)
                for func_call_hash, func_output in results}

    def get_cached_data_of_a_function_call(self, func_call_hash: str, func_name=None, use_isolated_connection=False) -> Optional[CacheData]:
        try:
            result = self.mongo.get_document_field(func_name, key=func_call_hash) if func_name else self.mongo.get_document_field(func_call_hash)
            func_output = self._serializer.loads(result)
            return CacheData(func_call_hash, func_output, func_name=func_name)
        except TypeError: return

    def save_cache_data(self, data: Dict[str, CacheData], use_isolated_connection=False) -> None:
        if len(data) == 0: return

        records = {}
        v = list(data.values())[0]
        if v.func_name:
            for func_call_hash, cache_data in data.items():
                if cache_data.func_name not in records: records[cache_data.func_name] = {}
                records[cache_data.func_name][func_call_hash] = self._serializer.dumps(cache_data.output)
            self.mongo.set_group_of_hashes(records)
        else:
            for func_call_hash, cache_data in data.items(): records[func_call_hash] = self._serializer.dumps(cache_data.output)
            self.mongo.set_group_of_key_value_pairs(records)
