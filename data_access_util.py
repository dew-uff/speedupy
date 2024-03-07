import os
from util import deserialize_from_file, serialize_to_file
from logger.log import debug, warn
from constantes import Constantes
from storage import remove

def get_file_name(func_call_hash:str):
    return "{0}.{1}".format(func_call_hash, "ipcache")

def deserialize(id):
    try:
        filename = os.path.join(Constantes().CACHE_FOLDER_NAME, get_file_name(id))
        deserialize_from_file(filename)
    except FileNotFoundError as e:
        warn("corrupt environment. Cache reference exists for a function in database but there is no file for it in cache folder. Have you deleted cache folder?")
        _autofix(id)
        return None

def _autofix(id):
    debug("starting autofix")
    debug("removing {0} from database".format(id))
    remove(get_file_name(id))
    debug("environment fixed")

def serialize(return_value, file_name):
    filename = os.path.join(Constantes().CACHE_FOLDER_NAME, get_file_name(file_name))
    serialize_to_file(return_value, filename)