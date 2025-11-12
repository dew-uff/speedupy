import mysql.connector


class BancoMySQL:
    database = 'speedupy'

    def __init__(self):
        self.conexao = None
        self.cursor = None
        try:
            self.conexao = mysql.connector.connect(host="127.0.0.1", user="root")
            self.cursor = self.conexao.cursor()
            self.cursor.execute(f"USE {self.database}")
        except mysql.connector.Error as err:
            if err.errno == 1049:
                # database does not exist!
                pass
            else:
                print(f"ERRO DE CONEXÃO COM MYSQL: {err}")
                self.conexao = None
                self.cursor = None

    def create_database(self):
        try:
            create_cache_table_sql = """
                CREATE TABLE IF NOT EXISTS CACHE (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    func_call_hash TEXT,
                    func_output BLOB,
                    func_name TEXT,
                    UNIQUE (func_call_hash(255))
                ) ENGINE=InnoDB;
            """
            self.cursor.execute(f"DROP DATABASE IF EXISTS {self.database}")
            self.cursor.execute(f"CREATE DATABASE {self.database}")
            self.cursor.execute(f"USE {self.database}")
            self.cursor.execute(create_cache_table_sql)
            self.conexao.commit()
        except mysql.connector.Error:
            self.conexao.rollback()

    def select(self, sql, arguments=()):
        if not self.cursor: return []
        try:
            self.cursor.execute(sql, arguments)
            return self.cursor.fetchall()
        except mysql.connector.Error:
            return []

    def exec_without_output(self, sql, arguments=()):
        if not self.cursor: return
        try:
            self.cursor.execute(sql, arguments)
        except mysql.connector.Error:
            self.conexao.rollback()

    def close_connection(self):
        if self.conexao and self.conexao.is_connected():
            self.cursor.close()
            self.conexao.close()

    def executemany_without_output(self, sql, arguments_list=()):
        if not self.cursor: return
        try:
            self.cursor.executemany(sql, arguments_list)
        except mysql.connector.Error as err:
            print(f"ERRO NO EXECUTEMANY MYSQL: {err}")
            self.conexao.rollback()

    def commit(self):
        self.conexao.commit()
