import mysql.connector
from mysql.connector import errorcode
# from SingletonMeta import SingletonMeta

class BancoMySQL: # (metaclass=SingletonMeta)
    def __init__(self):
        self.conexao = None
        self.cursor = None
        try:
            self.conexao = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="",
                database="speedupy"
            )
            self.cursor = self.conexao.cursor()
        except mysql.connector.Error as err:
            print(f"ERRO DE CONEXÃO COM MYSQL: {err}")
            self.conexao = None
            self.cursor = None

    def create_database(self):
        if not self.cursor: return
        create_cache_table_sql = """
        CREATE TABLE IF NOT EXISTS CACHE (
            id INT PRIMARY KEY AUTO_INCREMENT,
            func_call_hash TEXT,
            func_output BLOB,
            func_name TEXT,
            UNIQUE (func_call_hash(255))
        ) ENGINE=InnoDB;
        """
        try:
            self.cursor.execute(create_cache_table_sql)
            self.conexao.commit()
        except mysql.connector.Error as err:
            self.conexao.rollback()

    def select(self, sql, arguments=()):
        if not self.cursor: return []
        try:
            self.cursor.execute(sql, arguments)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            return []

    def exec_without_output(self, sql, arguments=()):
        if not self.cursor: return
        try:
            self.cursor.execute(sql, arguments)
            self.conexao.commit()
        except mysql.connector.Error as err:
            self.conexao.rollback()

    def close_connection(self):
        if hasattr(self, 'conexao') and self.conexao and self.conexao.is_connected():
            self.cursor.close()
            self.conexao.close()
            
    def executemany_without_output(self, sql, arguments_list=()):
        if not self.cursor: return
        try:
            self.cursor.executemany(sql, arguments_list)
            self.conexao.commit()
        except mysql.connector.Error as err:
            print(f"ERRO NO EXECUTEMANY MYSQL: {err}")
            self.conexao.rollback()