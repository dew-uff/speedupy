import os
import sys
import unittest
from unittest.mock import Mock

from mysql.connector import Error

project_folder = os.path.realpath(__file__).split("test/")[0]
sys.path.append(project_folder)

from entities.BancoMySQL import BancoMySQL


class TestExecuteManyWithoutOutput(unittest.TestCase):
    def setUp(self):
        self.banco = BancoMySQL()
        self.banco.cursor = Mock()
        self.banco.conexao = Mock()

    def test_splits_into_multiple_batches(self):
        self.banco._max_packet_size = 5000

        sql = "INSERT INTO test VALUES (%s, %s)"

        # Cada entry_size = 4096 + 1000 bytes = 5096
        value = b"x" * 1000

        arguments_list = [
            ("k1", value),
            ("k2", value),
            ("k3", value),
        ]

        self.banco.executemany_without_output(sql, arguments_list)

        self.assertEqual(self.banco.cursor.executemany.call_count, 3)
        self.banco.cursor.executemany.assert_any_call(sql, [("k1", value)])
        self.banco.cursor.executemany.assert_any_call(sql, [("k2", value)])
        self.banco.cursor.executemany.assert_any_call(sql, [("k3", value)])

    def test_single_batch(self):
        self.banco._max_packet_size = 20000  # Large enough

        sql = "INSERT INTO test VALUES (%s, %s)"
        value = b"x" * 1000

        arguments_list = [
            ("k1", value),
            ("k2", value),
        ]

        self.banco.executemany_without_output(sql, arguments_list)

        self.banco.cursor.executemany.assert_called_once_with(sql, arguments_list)

    def test_rollback_on_mysql_error(self):
        self.banco._max_packet_size = 20000
        self.banco.cursor.executemany.side_effect = Error("DB error")

        sql = "INSERT INTO test VALUES (%s, %s)"
        value = b"x" * 1000
        arguments_list = [("k1", value)]

        self.banco.executemany_without_output(sql, arguments_list)

        self.banco.conexao.rollback.assert_called_once()
