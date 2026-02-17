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
            self._get_max_packet_size()
        except mysql.connector.Error as err:
            if err.errno == 1049:
                # database does not exist!
                pass
            else:
                print(f"ERRO DE CONEXÃO COM MYSQL: {err}")
                self.conexao = None
                self.cursor = None

    def _get_max_packet_size(self):
        self.cursor.execute("SHOW VARIABLES LIKE 'max_allowed_packet'")
        result = self.cursor.fetchone()
        if result:
            limit_bytes = int(result[1])
            self._max_packet_size = int(limit_bytes * 0.8)
        else:
            self._max_packet_size = 16 * 1024 * 1024  # Default value (16MB)

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
        try:
            if not self.cursor: return []
            self.cursor.execute(sql, arguments)
            return self.cursor.fetchall()
        except mysql.connector.Error:
            return []

    def executemany_without_output(self, sql, arguments_list=()):
        try:
            if not self.cursor: return

            current_batch = []
            current_batch_size_bytes = 0
            SQL_METADATA = 4096
            for args in arguments_list:
                entry_size = SQL_METADATA + len(args[1])  # Estimates registry size
                if current_batch and (current_batch_size_bytes + entry_size > self._max_packet_size):
                    self.cursor.executemany(sql, current_batch)
                    current_batch = []
                    current_batch_size_bytes = 0

                current_batch.append(args)
                current_batch_size_bytes += entry_size

            if current_batch:
                self.cursor.executemany(sql, current_batch)
        except mysql.connector.Error:
            self.conexao.rollback()

    def commit(self):
        self.conexao.commit()

    def close_connection(self):
        if self.conexao and self.conexao.is_connected():
            self.cursor.close()
            self.conexao.close()
