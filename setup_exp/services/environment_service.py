import os

from constants import Constants
from entities.SQLiteDatabase import SQLiteDatabase
from logger.log import debug


def init_env(storage: str = "file"):
    """Prepare the environment for the given storage.

    Only that storage is touched. The other servers are never reached, and a
    driver is imported only when its storage is the chosen one.
    """
    debug("cheking if speedupy environment exists")
    if _env_exists():
        debug("environment already exists")
    else:
        debug("creating speedupy environment")
        _create_folder()
        _create_cache_folder()
    _create_databases(storage)


def _env_exists():
    return _folder_exists() and _cache_folder_exists()


def _folder_exists():
    return os.path.exists(Constants().FOLDER_NAME)


def _cache_folder_exists():
    return os.path.exists(Constants().CACHE_FOLDER_NAME)


def _create_folder():
    debug("creating .speedupy folder")
    if _folder_exists():
        debug(".speedupy folder already exists")
        return

    os.makedirs(Constants().FOLDER_NAME)


def _create_cache_folder():
    if _cache_folder_exists():
        debug("cache folder already exists")
        return

    debug("creating cache folder")
    os.makedirs(Constants().CACHE_FOLDER_NAME)


def _create_databases(storage: str = "file"):
    debug("creating database")
    if SQLiteDatabase.database_exists():
        debug("database already exists")
        return

    # Execution reads the SQLite FUNCTION_CALLS_PROV table whatever the
    # storage, and SQLite needs no server: it is always created.
    _initialize_storage(storage)
    _create_sqlite_database()


def _initialize_storage(storage: str):
    if storage == "redis":
        _flush_redis_database()
    if storage in ("mongo", "gridfs", "mongo-file", "mongo-gridfs"):
        _flush_mongo_database()
    if storage == "mysql":
        _create_mysql_database()


def _flush_mongo_database():
    # The mongo, gridfs, mongo-file and mongo-gridfs storages share the one
    # MongoDB database, `speedupy`: dropping it empties the collections of all
    # of them (MongoDatabase and GridFSDatabase drop the same database).
    from entities.MongoDatabase import MongoDatabase

    conexao_banco = MongoDatabase()
    conexao_banco.flush_database()


def _flush_redis_database():
    from entities.RedisDatabase import RedisDatabase

    redis = RedisDatabase()
    redis.flush_database()


def _create_mysql_database():
    from entities.MySQLDatabase import MySQLDatabase

    conexao_banco = MySQLDatabase()
    conexao_banco.create_database()
    conexao_banco.close_connection()


def _create_sqlite_database():
    conexao_banco = SQLiteDatabase()
    conexao_banco.create_database()
    conexao_banco.close_connection()
