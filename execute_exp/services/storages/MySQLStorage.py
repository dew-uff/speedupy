import pickle
from typing import Dict, Optional

from speedupy.execute_exp.services.storages.Storage import Storage
from speedupy.execute_exp.entitites.CacheData import CacheData
from speedupy.entities.BancoMySQL import BancoMySQL

class MySQLStorage(Storage):
    def __init__(self):
        self.db_connection = BancoMySQL()
        self.db_connection.create_database()

    def get_all_cached_data(self, use_isolated_connection=False) -> Dict[str, CacheData]:
        sql = "SELECT func_call_hash, func_output, func_name, id FROM CACHE"
        results = self.db_connection.select(sql)
        
        cache_data = {}
        for row in results:
            function_call_hash, output_blob, func_name, id = row
            output = pickle.loads(output_blob)
            cache_data[function_call_hash] = CacheData(function_call_hash, output, func_name, id)
            
        return cache_data

    def get_cached_data_of_a_function(self, func_name: str, use_isolated_connection=False) -> Dict[str, CacheData]:
        sql = "SELECT func_call_hash, func_output, id FROM CACHE WHERE func_name = %s"    
        results = self.db_connection.select(sql, (func_name,))
        
        cache_data = {}
        for row in results:
            function_call_hash, output_blob, id = row
            # Deserializa o resultado salvo no banco de dados
            output = pickle.loads(output_blob)
            cache_data[function_call_hash] = CacheData(function_call_hash, output, func_name, id)
            
        return cache_data

    def get_cached_data_of_a_function_call(self, func_call_hash: str, func_name=None, use_isolated_connection=False) -> Optional[CacheData]:
        try:
            sql = "SELECT func_output FROM CACHE WHERE func_call_hash = %s"
            result = self.db_connection.select(sql, (func_call_hash,))
            if result:
                func_output = pickle.loads(result[0][0])
                return CacheData(func_call_hash, func_output, func_name=func_name)
        except IndexError:
            return None
        return None

    def save_cache_data(self, data: Dict[str, CacheData], use_isolated_connection=False) -> None:
        if not data:
            return

        sql = """
            INSERT INTO CACHE (func_call_hash, func_output, func_name)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE func_output = VALUES(func_output);
        """
        
        sql_params = []
        for cache_entry in data.values():
            serialized_output = pickle.dumps(cache_entry.output)
            sql_params.append((
                cache_entry.function_call_hash,
                serialized_output,
                cache_entry.func_name
            ))
        
        if sql_params:
            self.db_connection.cursor.executemany(sql, sql_params)
            self.db_connection.conexao.commit()

    def __del__(self):
        if hasattr(self, 'db_connection'):
            self.db_connection.close_connection()