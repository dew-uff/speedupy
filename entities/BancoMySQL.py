import mysql.connector
from mysql.connector import errorcode
from SingletonMeta import SingletonMeta
import atexit

class BancoMySQL(metaclass=SingletonMeta):
    def __init__(self):
        """
        Estabelece a conexão com o servidor MySQL e garante que o banco de dados 'speedupy' exista.
        """
        try:
            self.conexao = mysql.connector.connect(
                host="localhost",
                user="root",
                password="" 
            )
            self.cursor = self.conexao.cursor()
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS speedupy")
            self.cursor.execute("USE speedupy")
            atexit.register(self.close_connection)
        except mysql.connector.Error as err:
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
        create_prov_table_sql = """
        CREATE TABLE IF NOT EXISTS FUNCTION_CALLS_PROV (
            id INT PRIMARY KEY AUTO_INCREMENT,
            function_call_hash TEXT NOT NULL,
            outputs BLOB NOT NULL,
            total_num_exec INT NOT NULL,
            next_revalidation INT NOT NULL,
            next_index_weighted_seq INT NOT NULL,
            mode_rel_freq REAL NOT NULL,
            mode_output BLOB NOT NULL,
            weighted_output_seq BLOB NOT NULL,
            mean_output BLOB NOT NULL,
            confidence_lv REAL NOT NULL,
            confidence_low_limit REAL NOT NULL,
            confidence_up_limit REAL NOT NULL,
            confidence_error REAL NOT NULL
        ) ENGINE=InnoDB;
        """
        try:
            self.cursor.execute(create_cache_table_sql)
            self.cursor.execute(create_prov_table_sql)
            self.conexao.commit()
        except mysql.connector.Error as err:
            self.conexao.rollback()

    def flush_database(self):
        if not self.cursor:
            return
        try:
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            self.cursor.execute("TRUNCATE TABLE CACHE;")
            self.cursor.execute("TRUNCATE TABLE FUNCTION_CALLS_PROV;")
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            self.conexao.commit()
        except mysql.connector.Error as err:
            if 'Unknown table' in err.msg:
                print("Tabelas ainda não existem, nada para limpar.")
            else:
                print(f"Erro ao limpar tabelas do MySQL: {err}")
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