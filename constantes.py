import os
import threading
from threading import Lock

from banco import Banco
from parser_params import get_params

class SingletonMeta(type):
    """
    Classe thread-safe para implementar Singleton.
    """
    _instances = {}
    _lock: Lock = Lock()
    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Constantes(metaclass=SingletonMeta):
    def __init__(self):
        self.g_argsp_m, self.g_argsp_M, self.g_argsp_s, self.g_argsp_no_cache, self.g_argsp_hash = get_params()
        
        self.CONEXAO_BANCO = None
        if self.g_argsp_m != ['v01x']:
            try:
                self.CONEXAO_BANCO = Banco(os.path.join(".intpy", "intpy.db"))
            except: #Need for unit testing!
                self.CONEXAO_BANCO = None
        
        self.DATA_DICTIONARY = {}
        self.NEW_DATA_DICTIONARY = {}
        self.FUNCTIONS_ALREADY_SELECTED_FROM_DB = []
        self.CACHED_DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()
