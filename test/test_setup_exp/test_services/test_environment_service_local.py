import os
import socket
import unittest
from pathlib import Path
from unittest.mock import patch

from entities.SQLiteDatabase import SQLiteDatabase
from setup_exp.services.environment_service import (
    _cache_folder_exists,
    _create_cache_folder,
    _create_databases,
    _create_folder,
    _env_exists,
    _folder_exists,
    init_env,
)


class TestEnvironmentServiceWithoutServers(unittest.TestCase):
    """The folder and SQLite parts of the environment: no server is needed."""

    FOLDER_NAME = ".speedupy"
    CACHE_FOLDER_NAME = os.path.join(FOLDER_NAME, "cache")
    SQLITE_DB_FILENAME = os.path.join(FOLDER_NAME, "speedupy.db")

    def setUp(self):
        os.system("rm -rf {}".format(self.FOLDER_NAME))
        self.addCleanup(os.system, "rm -rf {}".format(self.FOLDER_NAME))
        # No server is reachable, and none is touched when one is running.
        patcher = patch.object(
            socket.socket,
            "connect",
            side_effect=ConnectionRefusedError("no server in this test"),
        )
        self.connect = patcher.start()
        self.addCleanup(patcher.stop)

    def assert_sqlite_db_exists(self):
        self.assertTrue(os.path.exists(self.SQLITE_DB_FILENAME))
        expeceted_result = {("sqlite_sequence",), ("CACHE",), ("FUNCTION_CALLS_PROV",)}
        SQLiteDatabase.db_path = self.SQLITE_DB_FILENAME
        conexao_banco = SQLiteDatabase()
        resp = conexao_banco.select(
            "SELECT tbl_name FROM sqlite_master WHERE type = 'table'"
        )
        self.assertSetEqual(set(resp), expeceted_result)

    # Moved from test_environment_service.py, unchanged.

    def test_cache_folder_exists_when_cache_folder_exists(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        self.assertTrue(_cache_folder_exists())

    def test_cache_folder_exists_when_cache_folder_does_not_exist(self):
        self.assertFalse(_cache_folder_exists())

    def test_db_exists_when_db_exists(self):
        os.mkdir(self.FOLDER_NAME)
        Path(self.SQLITE_DB_FILENAME).touch()
        self.assertTrue(SQLiteDatabase.database_exists())

    def test_db_exists_when_db_does_not_exist(self):
        self.assertFalse(SQLiteDatabase.database_exists())

    def test_folder_exists_when_folder_exists(self):
        os.mkdir(self.FOLDER_NAME)
        self.assertTrue(_folder_exists())

    def test_folder_exists_when_folder_does_not_exist(self):
        self.assertFalse(_folder_exists())

    def test_env_exists_when_env_exists(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        Path(self.SQLITE_DB_FILENAME).touch()
        self.assertTrue(_env_exists())

    def test_env_exists_when_env_does_not_exist(self):
        self.assertFalse(_env_exists())

    def test_create_cache_folder(self):
        self.assertFalse(os.path.exists(self.CACHE_FOLDER_NAME))
        _create_cache_folder()
        self.assertTrue(os.path.exists(self.CACHE_FOLDER_NAME))

    def test_create_folder(self):
        self.assertFalse(os.path.exists(self.FOLDER_NAME))
        _create_folder()
        self.assertTrue(os.path.exists(self.FOLDER_NAME))

    # init_env keeps its two tests, which need no server now that the default
    # storage is `file`.

    def test_init_env_when_env_does_not_exist(self):
        init_env()
        self.assertTrue(os.path.exists(self.CACHE_FOLDER_NAME))
        self.assert_sqlite_db_exists()
        self.connect.assert_not_called()

    def test_init_env_when_env_partially_exists(self):
        os.mkdir(self.FOLDER_NAME)
        init_env()
        self.assertTrue(os.path.exists(self.CACHE_FOLDER_NAME))
        self.assert_sqlite_db_exists()
        self.connect.assert_not_called()

    # New: what D2 changes.

    def test_env_exists_when_only_the_folder_exists(self):
        # Replaces test_env_exists_when_env_partially_not_exist, which built the
        # cache folder and expected False because the SQLite file was missing.
        os.mkdir(self.FOLDER_NAME)
        self.assertFalse(_env_exists())

    def test_env_exists_does_not_require_the_sqlite_file(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        self.assertFalse(os.path.exists(self.SQLITE_DB_FILENAME))
        self.assertTrue(_env_exists())

    def test_init_env_creates_the_sqlite_file_when_only_the_folders_exist(self):
        os.makedirs(self.CACHE_FOLDER_NAME)
        init_env("file")
        self.assert_sqlite_db_exists()
        self.connect.assert_not_called()

    def test_create_databases_with_a_storage_that_has_no_server(self):
        for storage in ("file", "sqlite"):
            with self.subTest(storage=storage):
                os.system("rm -rf {}".format(self.FOLDER_NAME))
                os.mkdir(self.FOLDER_NAME)
                _create_databases(storage)
                self.assert_sqlite_db_exists()
                self.connect.assert_not_called()

    def test_create_databases_when_sqlite_database_exists_touches_no_server(self):
        os.mkdir(self.FOLDER_NAME)
        Path(self.SQLITE_DB_FILENAME).touch()
        for storage in ("redis", "mongo", "gridfs", "mysql"):
            with self.subTest(storage=storage):
                _create_databases(storage)
                self.connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
