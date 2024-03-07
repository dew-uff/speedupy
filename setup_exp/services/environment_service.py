import os
from banco import Banco
from logger.log import debug
from constantes import Constantes

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
    return _folder_exists() and _db_exists() and _cache_folder_exists()


def _folder_exists():
    return os.path.exists(Constantes().FOLDER_NAME)


def _db_exists():
    return os.path.isfile(Constantes().BD_PATH)


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


def _create_database():
    debug("creating database")
    if _db_exists():
        debug("database already exists")
        return
    conexaoBanco = Banco(Constantes().BD_PATH)
    _create_table_CACHE(conexaoBanco)
    _create_table_FUNCTION_CALLS_PROV(conexaoBanco)
    conexaoBanco.fecharConexao()


def _create_table_CACHE(banco: Banco):
    debug("creating table CACHE")

    stmt = "CREATE TABLE IF NOT EXISTS CACHE (\
    id INTEGER PRIMARY KEY AUTOINCREMENT,\
    func_call_hash TEXT UNIQUE,\
    func_output BLOB,\
    func_name TEXT\
    );"

    banco.executarComandoSQLSemRetorno(stmt)

def _create_table_FUNCTION_CALLS_PROV(banco: Banco):
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

    banco.executarComandoSQLSemRetorno(stmt)
