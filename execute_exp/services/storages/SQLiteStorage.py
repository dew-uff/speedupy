import threading
from typing import Dict, Optional

from entities.BancoSQLite import BancoSQLite
from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.Storage import Storage


class SQLiteStorage(Storage):
    def __init__(self, serializer: Serializer):
        super().__init__(serializer)
        self.__local = threading.local()
        self.__local.db_connection = BancoSQLite()

    def _set_db_connection(func):
        def wrapper(self, *args, use_isolated_connection=False, **kwargs):
            if use_isolated_connection:
                self.__local.previous_conn = self.__local.db_connection
                self.__local.db_connection = BancoSQLite()
                result = func(
                    self,
                    *args,
                    **kwargs,
                    use_isolated_connection=use_isolated_connection,
                )
                self.__local.db_connection.close_connection()
                self.__local.db_connection = self.__local.previous_conn
            else:
                result = func(
                    self,
                    *args,
                    **kwargs,
                    use_isolated_connection=use_isolated_connection,
                )
            return result

        return wrapper

    @_set_db_connection
    def get_all_cached_data(
        self, use_isolated_connection=False
    ) -> Dict[str, CacheData]:
        results = self.__local.db_connection.select(
            "SELECT func_call_hash, func_output FROM CACHE"
        )
        data = {
            func_call_hash: CacheData(
                func_call_hash, self._serializer.loads(func_output)
            )
            for func_call_hash, func_output in results
        }
        return data

    @_set_db_connection
    def get_cached_data_of_a_function(
        self, func_name: str, use_isolated_connection=False
    ) -> Dict[str, CacheData]:
        results = self.__local.db_connection.select(
            "SELECT func_call_hash, func_output FROM CACHE WHERE func_name = ?",
            (func_name,),
        )
        data = {
            func_call_hash: CacheData(
                func_call_hash, self._serializer.loads(func_output), func_name=func_name
            )
            for func_call_hash, func_output in results
        }
        return data

    @_set_db_connection
    def get_cached_data_of_a_function_call(
        self, func_call_hash: str, func_name=None, use_isolated_connection=False
    ) -> Optional[CacheData]:
        try:
            result = self.__local.db_connection.select(
                "SELECT func_output FROM CACHE WHERE func_call_hash = ?",
                (func_call_hash,),
            )
            func_output = self._serializer.loads(result[0][0])
            return CacheData(func_call_hash, func_output, func_name=func_name)
        except IndexError:
            pass

    @_set_db_connection
    def save_cache_data(
        self, data: Dict[str, CacheData], use_isolated_connection=False
    ) -> None:
        if len(data) == 0:
            return
        sql_stmt = ""
        sql_params = []
        for func_call_hash, cache_data in data.items():
            func_output = self._serializer.dumps(cache_data.output)
            sql_params.append(func_call_hash)
            sql_params.append(func_output)
            if cache_data.func_name:
                sql_params.append(cache_data.func_name)
        if list(data.values())[
            0
        ].func_name:  # Testing if data records have func_name set or not!
            sql_stmt = (
                "INSERT OR IGNORE INTO CACHE(func_call_hash, func_output, func_name) VALUES"
                + len(data) * " (?, ?, ?),"
            )
        else:
            sql_stmt = (
                "INSERT OR IGNORE INTO CACHE(func_call_hash, func_output) VALUES"
                + len(data) * " (?, ?),"
            )
        sql_stmt = sql_stmt[:-1]
        self.__local.db_connection.exec_without_output(sql_stmt, sql_params)
        # Commit here, on the connection that wrote (the isolated one when it
        # is used): nothing may wait for the instance to be finalized, which
        # Python does not guarantee at interpreter exit (issue #86).
        self.__local.db_connection.commit()
