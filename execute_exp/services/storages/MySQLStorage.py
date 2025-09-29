import pickle
from typing import Dict, Optional

from execute_exp.services.storages.Storage import Storage
from execute_exp.entitites.CacheData import CacheData
from entities.BancoMySQL import BancoMySQL

class MySQLStorage(Storage):
    def __init__(self, db_connection=None):
        if db_connection:
            # Usado pelos testes, que "injetam" a conexão
            self.db_connection = db_connection
        else:
            # Usado pela execução manual, cria a própria conexão
            self.db_connection = BancoMySQL()
        
        # A criação das tabelas deve ser chamada aqui para ambos os casos
        self.db_connection.create_database()

    def get_all_cached_data(self, use_isolated_connection=False) -> Dict[str, CacheData]:
        sql = "SELECT func_call_hash, func_output, func_name FROM CACHE"
        results = self.db_connection.select(sql)
        
        cache_data = {}
        for row in results:
            function_call_hash, output_blob, func_name = row
            try:
                output = pickle.loads(output_blob)
                cache_data[function_call_hash] = CacheData(function_call_hash, output, func_name)
            except Exception:
                continue # Ignora dados inválidos
            
        return cache_data

    def get_cached_data_of_a_function(self, func_name: str, use_isolated_connection=False) -> Dict[str, CacheData]:
        sql = "SELECT func_call_hash, func_output FROM CACHE WHERE func_name = %s"
        results = self.db_connection.select(sql, (func_name,))
        
        cache_data = {}
        for row in results:
            function_call_hash, output_blob = row
            try:
                output = pickle.loads(output_blob)
                cache_data[function_call_hash] = CacheData(function_call_hash, output, func_name)
            except Exception:
                continue # Ignora dados inválidos
            
        return cache_data

    def get_cached_data_of_a_function_call(self, func_call_hash: str, func_name=None, use_isolated_connection=False) -> Optional[CacheData]:
        try:
            sql = "SELECT func_output FROM CACHE WHERE func_call_hash = %s"
            result = self.db_connection.select(sql, (func_call_hash,))
            if result:
                func_output = pickle.loads(result[0][0])
                return CacheData(func_call_hash, func_output, func_name=func_name)
        except Exception:
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
        
        sql_params = [
            (
                cache_entry.function_call_hash,
                pickle.dumps(cache_entry.output),
                cache_entry.func_name
            ) for cache_entry in data.values()
        ]
        
        if not sql_params:
            return
            
        try:
            self.db_connection.cursor.executemany(sql, sql_params)
            self.db_connection.conexao.commit()
        except Exception as e:
            print(f"ERRO AO SALVAR DADOS NO MYSQL: {e}")
            self.db_connection.conexao.rollback()