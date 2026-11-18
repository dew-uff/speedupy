import os
import sqlite3

from constants import Constants


class SQLiteDatabase:
    db_path = Constants().DB_PATH

    @classmethod
    def database_exists(cls):
        return os.path.isfile(cls.db_path)

    def __init__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def create_database(self):
        self._create_table_CACHE()
        self._create_table_FUNCTION_CALLS_PROV()

    def _create_table_CACHE(self):
        stmt = "CREATE TABLE IF NOT EXISTS CACHE (\
		id INTEGER PRIMARY KEY AUTOINCREMENT,\
		func_call_hash TEXT UNIQUE,\
		func_output BLOB,\
		func_name TEXT\
		);"

        self.exec_without_output(stmt)

    def _create_table_FUNCTION_CALLS_PROV(self):
        stmt = "CREATE TABLE FUNCTION_CALLS_PROV(\
		id INTEGER PRIMARY KEY AUTOINCREMENT,\
		function_call_hash TEXT NOT NULL,\
		outputs BLOB NOT NULL,\
		total_num_exec INTEGER NOT NULL,\
		next_revalidation INTEGER NOT NULL,\
		next_index_weighted_seq INTEGER NOT NULL,\
		mode_rel_freq REAL NOT NULL,\
		mode_output BLOB NOT NULL,\
		weighted_output_seq BLOB NOT NULL,\
		mean_output BLOB NOT NULL,\
		confidence_lv REAL NOT NULL,\
		confidence_low_limit REAL NOT NULL,\
		confidence_up_limit REAL NOT NULL,\
		confidence_error REAL NOT NULL\
		);"

        self.exec_without_output(stmt)

    def exec_without_output(self, sql, arguments=()):
        self.cursor.execute(sql, arguments)

    def select(self, sql, arguments=()):
        self.cursor.execute(sql, arguments)
        return self.cursor.fetchall()

    def commit(self):
        self.connection.commit()

    def close_connection(self):
        self.connection.close()
