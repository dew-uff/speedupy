import os
from logger.log import debug
from constantes import Constantes
from entities.BancoSQLite import BancoSQLite
from entities.BancoRedis import BancoRedis
from entities.BancoMongo import BancoMongo


def init_env(storage_type: str = 'file'):
    debug("cheking if speedupy environment exists")
    if _env_exists():
        debug("environment already exists")
        return

    debug("creating speedupy environment")
    _create_folder()
    _create_cache_folder()
    _create_sqlite_database()
    _create_databases(storage_type)


def _env_exists():
    return _folder_exists() and \
           _cache_folder_exists() and \
           BancoSQLite.database_exists()


def _folder_exists():
    return os.path.exists(Constantes().FOLDER_NAME)


def _cache_folder_exists():
    return os.path.exists(Constantes().CACHE_FOLDER_NAME)


def _create_folder():
    debug("creating .speedupy folder")
    if _folder_exists():
        debug(".speedupy folder already exists")
        return

    os.makedirs(Constantes().FOLDER_NAME)


def _create_cache_folder():
    if _cache_folder_exists():
        debug("cache folder already exists")
        return

    debug("creating cache folder")
    os.makedirs(Constantes().CACHE_FOLDER_NAME)

def _create_databases(storage_type: str):
    debug(f"checking and initializing database for storage type: {storage_type}")

    if storage_type == 'redis':
        _flush_redis_database()
        
    elif storage_type == 'mongo':
        _flush_mongo_database()

    #elif storage_type == 'sqlite':
    #    if BancoSQLite.database_exists():
    #        debug("SQLite database already exists")
    #        return
    #    _create_sqlite_database()
        
    elif storage_type == 'file':
        debug("Filesystem storage requires no special database initialization.")


def _flush_mongo_database():
    conexao_banco = BancoMongo()
    conexao_banco.flush_database()


def _flush_redis_database():
    redis = BancoRedis()
    redis.flush_database()


def _create_sqlite_database():
    conexao_banco = BancoSQLite()
    conexao_banco.create_database()
    conexao_banco.close_connection()
