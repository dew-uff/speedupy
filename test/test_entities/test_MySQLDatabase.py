import unittest
from unittest.mock import Mock

from mysql.connector import Error

from entities.MySQLDatabase import MySQLDatabase


class TestExecuteManyWithoutOutput(unittest.TestCase):
    def setUp(self):
        self.database = MySQLDatabase()
        self.database.cursor = Mock()
        self.database.connection = Mock()

    def test_splits_into_multiple_batches(self):
        self.database._max_packet_size = 5000

        sql = "INSERT INTO test VALUES (%s, %s)"

        # Each entry_size = 4096 + 1000 bytes = 5096
        value = b"x" * 1000

        arguments_list = [
            ("k1", value),
            ("k2", value),
            ("k3", value),
        ]

        self.database.executemany_without_output(sql, arguments_list)

        self.assertEqual(self.database.cursor.executemany.call_count, 3)
        self.database.cursor.executemany.assert_any_call(sql, [("k1", value)])
        self.database.cursor.executemany.assert_any_call(sql, [("k2", value)])
        self.database.cursor.executemany.assert_any_call(sql, [("k3", value)])

    def test_single_batch(self):
        self.database._max_packet_size = 20000  # Large enough

        sql = "INSERT INTO test VALUES (%s, %s)"
        value = b"x" * 1000

        arguments_list = [
            ("k1", value),
            ("k2", value),
        ]

        self.database.executemany_without_output(sql, arguments_list)

        self.database.cursor.executemany.assert_called_once_with(sql, arguments_list)

    def test_rollback_on_mysql_error(self):
        self.database._max_packet_size = 20000
        self.database.cursor.executemany.side_effect = Error("DB error")

        sql = "INSERT INTO test VALUES (%s, %s)"
        value = b"x" * 1000
        arguments_list = [("k1", value)]

        self.database.executemany_without_output(sql, arguments_list)

        self.database.connection.rollback.assert_called_once()
