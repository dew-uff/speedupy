import os
from banco import Banco

from logger.log import debug

FOLDER_NAME = ".intpy"
CACHE_FOLDER_NAME = FOLDER_NAME + "/cache"

def _create_table_FUNCTION_PARAMS(banco: Banco):
    debug("creating table FUNCTION_PARAMS")
    
    stmt = "CREATE TABLE IF NOT FUNCTION_PARAMS (\
    id INTEGER PRIMARY KEY AUTOINCREMENT,\
    function_call_id INTEGER NOT NULL,\
    function_hash TEXT NOT NULL,\
    parameter_value BLOB NOT NULL,\
    parameter_name TEXT NOT NULL,\
    is_keyword_param BOOLEAN NOT NULL,\
    parameter_position INTEGER NOT NULL,\
    FOREIGN KEY (function_hash) REFERENCES METADATA(function_hash)\
    );"

    banco.executarComandoSQLSemRetorno(stmt)


def _create_table_METADATA(banco: Banco):
    debug("creating table METADATA")
    
    stmt = "CREATE TABLE IF NOT EXISTS METADATA (\
    id INTEGER PRIMARY KEY AUTOINCREMENT,\
    function_hash TEXT NOT NULL,\
    return_value BLOB NOT NULL,\
    execution_time REAL NOT NULL,\
    );"

    banco.executarComandoSQLSemRetorno(stmt)


def _create_table_CACHE(banco: Banco):
    debug("creating table CACHE")

    stmt = "CREATE TABLE IF NOT EXISTS CACHE (\
    id INTEGER PRIMARY KEY AUTOINCREMENT,\
    cache_file TEXT UNIQUE,\
    fun_name TEXT\
    );"

    banco.executarComandoSQLSemRetorno(stmt)


def _create_database():
    debug("creating database")
    if _db_exists():
        debug("database already exists")
        return
    conexaoBanco = Banco('.intpy/intpy.db')
    _create_table_CACHE(conexaoBanco)
    _create_table_METADATA(conexaoBanco)
    _create_table_FUNCTION_PARAMS(conexaoBanco)
    conexaoBanco.fecharConexao()


def _create_cache_folder():
    if _cache_folder_exists():
        debug("cache folder already exists")
        return

    debug("creating cache folder")
    os.makedirs(CACHE_FOLDER_NAME)


def _create_folder():
    debug("creating .intpy folder")
    if _folder_exists():
        debug(".intpy folder already exists")
        return

    os.makedirs(FOLDER_NAME)


def _cache_folder_exists():
    return os.path.exists(CACHE_FOLDER_NAME)


def _db_exists():
    return os.path.isfile('.intpy/intpy.db')


def _folder_exists():
    return os.path.exists(FOLDER_NAME)


def _env_exists():
    return _folder_exists() and _db_exists() and _cache_folder_exists()


def init_env():
    debug("cheking if intpy environment exists")
    if _env_exists():
        debug("environment already exists")
        return

    debug("creating intpy environment")
    _create_folder()
    _create_cache_folder()
    _create_database()
