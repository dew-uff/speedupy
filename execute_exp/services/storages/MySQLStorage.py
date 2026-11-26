from typing import Dict, Optional

from entities.MySQLDatabase import MySQLDatabase
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.Storage import Storage


class MySQLStorage(Storage):
    def __init__(self, serializer: Serializer):
        super().__init__(serializer)
        self.db_connection = MySQLDatabase()

    def get_all_cached_data(
        self, use_isolated_connection=False
    ) -> Dict[str, CacheData]:
        sql = "SELECT func_call_hash, func_output FROM CACHE"
        results = self.db_connection.select(sql)

        cache_data = {}
        for row in results:
            function_call_hash, output_blob = row
            try:
                output = self._serializer.loads(output_blob)
                cache_data[function_call_hash] = CacheData(function_call_hash, output)
            # A row that cannot be loaded is a cache miss, on purpose.
            except Exception:  # nosec B112
                continue  # Ignore invalid data

        return cache_data

    def get_cached_data_of_a_function(
        self, func_name: str, use_isolated_connection=False
    ) -> Dict[str, CacheData]:
        sql = "SELECT func_call_hash, func_output FROM CACHE WHERE func_name = %s"
        results = self.db_connection.select(sql, (func_name,))

        cache_data = {}
        for row in results:
            function_call_hash, output_blob = row
            try:
                output = self._serializer.loads(output_blob)
                cache_data[function_call_hash] = CacheData(
                    function_call_hash, output, func_name
                )
            # A row that cannot be loaded is a cache miss, on purpose.
            except Exception:  # nosec B112
                continue  # Ignore invalid data

        return cache_data

    def get_cached_data_of_a_function_call(
        self, func_call_hash: str, func_name=None, use_isolated_connection=False
    ) -> Optional[CacheData]:
        try:
            sql = "SELECT func_output FROM CACHE WHERE func_call_hash = %s"
            result = self.db_connection.select(sql, (func_call_hash,))
            if result:
                func_output = self._serializer.loads(result[0][0])
                return CacheData(func_call_hash, func_output, func_name=func_name)
        except Exception:
            return None
        return None

    def save_cache_data(
        self, data: Dict[str, CacheData], use_isolated_connection=False
    ) -> None:
        if not data:
            return

        sql = """
            INSERT INTO CACHE (func_call_hash, func_output, func_name)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE func_output = VALUES(func_output);
        """

        sql_params = [
            (
                cache_entry.function_call_hash,
                self._serializer.dumps(cache_entry.output),
                cache_entry.func_name,
            )
            for cache_entry in data.values()
        ]

        if not sql_params:
            return

        self.db_connection.executemany_without_output(sql, sql_params)
        self.db_connection.commit()
