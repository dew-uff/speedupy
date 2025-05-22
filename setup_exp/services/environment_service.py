import os
from logger.log import debug
from constantes import Constantes
from entities.BancoSQLite import BancoSQLite
from BancoRedis import BancoRedis


def init_env():
    debug("cheking if speedupy environment exists")
    if _env_exists():
        debug("environment already exists")
        return

    debug("creating speedupy environment")
    _create_folder()
    _create_cache_folder()
    _create_database()


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

# XXX: TESTAR!
def _create_database():
    debug("creating database")
    if BancoSQLite.database_exists():
        debug("database already exists")
        return

    __flush_redis_database()
    __create_sqlite_database()

# XXX: TESTAR!
def __flush_redis_database():
    redis = BancoRedis()
    redis.flushDatabase()
    redis.closeConnection()


def __create_sqlite_database():
    conexao_banco = BancoSQLite()
    conexao_banco.create_database()
    conexao_banco.fechar_conexao()
