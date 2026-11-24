"""A server backend whose server cannot be reached fails with one clear error.

No server is needed: each driver call that probes the server is patched to
fail. The success path is held by the server tests (``SPEEDUPY_TEST_SERVERS=1``).
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

import mysql.connector
import pymemcache.client.base
import pymongo.database
import pymongo.errors
import redis
import redis.exceptions

from entities.GridFSDatabase import GridFSDatabase
from entities.MemcachedDatabase import MemcachedDatabase
from entities.MongoDatabase import MongoDatabase
from entities.MySQLDatabase import MySQLDatabase
from entities.RedisDatabase import RedisDatabase
from entities.server_errors import ServerUnreachableError
from execute_exp.services import factory
from setup_exp.services import environment_service

REDIS_ERROR = redis.exceptions.ConnectionError("Connection refused")
MONGO_ERROR = pymongo.errors.ServerSelectionTimeoutError("localhost:27017: refused")
MYSQL_ERROR = mysql.connector.Error("Can't connect to MySQL server", errno=2003)
MEMCACHED_ERROR = ConnectionRefusedError(111, "Connection refused")

# entity, the patch that makes its probe fail, the error it raises, and what
# the message must name: backend, address, compose profile, install page.
CASES = {
    "redis": (
        RedisDatabase,
        lambda: patch.object(redis.Redis, "ping", side_effect=REDIS_ERROR),
        REDIS_ERROR,
        ("The redis backend", "localhost:6379", "--profile redis", "redis.io"),
    ),
    "mongo": (
        MongoDatabase,
        lambda: patch.object(
            pymongo.database.Database, "command", side_effect=MONGO_ERROR
        ),
        MONGO_ERROR,
        (
            "The mongo backend",
            "localhost:27017",
            "--profile mongo",
            "mongodb.com/docs/manual/installation",
        ),
    ),
    "gridfs": (
        GridFSDatabase,
        lambda: patch.object(
            pymongo.database.Database, "command", side_effect=MONGO_ERROR
        ),
        MONGO_ERROR,
        (
            "The gridfs backend",
            "localhost:27017",
            "--profile mongo",
            "mongodb.com/docs/manual/installation",
        ),
    ),
    "mysql": (
        MySQLDatabase,
        lambda: patch.object(mysql.connector, "connect", side_effect=MYSQL_ERROR),
        MYSQL_ERROR,
        (
            "The mysql backend",
            "127.0.0.1:3306",
            "--profile mysql",
            "dev.mysql.com/doc/refman/en/installing.html",
        ),
    ),
    "memcached": (
        MemcachedDatabase,
        lambda: patch.object(
            pymemcache.client.base.Client, "version", side_effect=MEMCACHED_ERROR
        ),
        MEMCACHED_ERROR,
        (
            "The memcached backend",
            "localhost:11211",
            "--profile memcached",
            "memcached.org/downloads",
        ),
    ),
}


class TestUnreachableServers(unittest.TestCase):
    def assert_names_backend_address_and_alternatives(self, name):
        entity, failing_probe, _error, expected = CASES[name]
        with failing_probe():
            with self.assertRaises(ServerUnreachableError) as raised:
                entity()

        message = str(raised.exception)
        for text in expected:
            self.assertIn(text, message)
        self.assertIn("which is not reachable", message)
        self.assertIn("docker compose --profile", message)
        self.assertIn("up -d --wait", message)
        self.assertIn("-s file or -s sqlite", message)

    def test_redis_names_the_backend_the_address_and_the_alternatives(self):
        self.assert_names_backend_address_and_alternatives("redis")

    def test_mongo_names_the_backend_the_address_and_the_alternatives(self):
        self.assert_names_backend_address_and_alternatives("mongo")

    def test_gridfs_names_the_backend_the_address_and_the_alternatives(self):
        self.assert_names_backend_address_and_alternatives("gridfs")

    def test_mysql_names_the_backend_the_address_and_the_alternatives(self):
        self.assert_names_backend_address_and_alternatives("mysql")

    def test_memcached_names_the_backend_the_address_and_the_alternatives(self):
        self.assert_names_backend_address_and_alternatives("memcached")

    def test_the_error_is_a_connection_error_raised_from_the_drivers_error(self):
        for name, (entity, failing_probe, error, _expected) in CASES.items():
            with self.subTest(backend=name):
                with failing_probe():
                    with self.assertRaises(ConnectionError) as raised:
                        entity()

                self.assertIsInstance(raised.exception, ServerUnreachableError)
                self.assertIs(raised.exception.__cause__, error)

    def test_a_mysql_error_other_than_unreachable_shows_the_drivers_text(self):
        refused = mysql.connector.Error("Access denied for user 'root'", errno=1045)
        with patch.object(mysql.connector, "connect", side_effect=refused):
            with self.assertRaises(ServerUnreachableError) as raised:
                MySQLDatabase()

        self.assertIn("The driver said: ", str(raised.exception))
        self.assertIn("Access denied for user 'root'", str(raised.exception))

    def test_mysql_without_the_database_still_connects(self):
        # Error 1049 (unknown database) is expected before the first setup.
        connection = MagicMock()
        connection.cursor.return_value.execute.side_effect = mysql.connector.Error(
            "Unknown database 'speedupy'", errno=1049
        )
        with patch.object(mysql.connector, "connect", return_value=connection):
            database = MySQLDatabase()

        self.assertIs(database.connection, connection)

    def test_execution_reports_it_when_the_storage_is_built(self):
        settings = Mock(storage=["redis"], serializer=["pickle"])
        with patch.object(factory, "SpeeduPySettings", return_value=settings):
            with patch.object(redis.Redis, "ping", side_effect=REDIS_ERROR):
                with self.assertRaises(ServerUnreachableError) as raised:
                    factory._init_storage()

        self.assertIn("The redis backend", str(raised.exception))
        self.assertIn("docker compose --profile redis", str(raised.exception))

    def test_setup_reports_it_when_the_storage_is_prepared(self):
        with patch.object(redis.Redis, "ping", side_effect=REDIS_ERROR):
            with patch.object(redis.Redis, "flushdb") as flushdb:
                with self.assertRaises(ServerUnreachableError) as raised:
                    environment_service._initialize_storage("redis")

        flushdb.assert_not_called()
        self.assertIn("The redis backend", str(raised.exception))
        self.assertIn("-s file or -s sqlite", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
