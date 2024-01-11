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

        self.FOLDER_NAME = ".intpy"
        self.CACHE_FOLDER_NAME = os.path.join(self.FOLDER_NAME, "cache")
        self.BD_PATH = os.path.join(self.FOLDER_NAME, "intpy.db")
        
        self.TEMP_FOLDER = '.intpy_temp'
        self.EXP_FUNCTIONS_FILENAME = os.path.join(self.TEMP_FOLDER, 'functions_intpy.json')
        
        self.__CONEXAO_BANCO = None
        self.DATA_DICTIONARY = {}
        self.NEW_DATA_DICTIONARY = {}
        self.FUNCTIONS_ALREADY_SELECTED_FROM_DB = []
        self.CACHED_DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()

    def set_paths_for_executing_inside_main_folder(self):
        self.FOLDER_NAME = ".intpy"
        self.CACHE_FOLDER_NAME = os.path.join(self.FOLDER_NAME, "cache")
        self.BD_PATH = os.path.join(self.FOLDER_NAME, "intpy.db")
        
        self.EXP_FUNCTIONS_FILENAME = os.path.join(self.TEMP_FOLDER, 'functions_intpy.json')
        
    def set_paths_for_executing_inside_temp_folder(self):
        self.FOLDER_NAME = os.path.join("..", ".intpy")
        self.CACHE_FOLDER_NAME = os.path.join(self.FOLDER_NAME, "cache")
        self.BD_PATH = os.path.join(self.FOLDER_NAME, "intpy.db")
        
        self.EXP_FUNCTIONS_FILENAME = 'functions_intpy.json'

    @property
    def CONEXAO_BANCO(self):
        if self.g_argsp_m != ['v01x'] and self.__CONEXAO_BANCO is None:
            try:
                self.__CONEXAO_BANCO = Banco(self.BD_PATH)
            except: #Need for unit testing!
                self.__CONEXAO_BANCO = None
        return self.__CONEXAO_BANCO

    @CONEXAO_BANCO.setter
    def CONEXAO_BANCO(self, CONEXAO_BANCO):
        self.__CONEXAO_BANCO = CONEXAO_BANCO
