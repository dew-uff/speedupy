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
        self.g_argsp_exp_args,\
        self.g_argsp_m, \
        self.g_argsp_M, \
        self.g_argsp_s, \
        self.g_argsp_exec_mode, \
        self.g_argsp_strategy, \
        self.g_argsp_revalidation, \
        self.g_argsp_min_num_exec, \
        self.g_argsp_min_mode_occurrence, \
        self.g_argsp_confidence_level, \
        self.g_argsp_max_error_per_function, \
        self.g_argsp_hash, \
        self.g_argsp_inputs, \
        self.g_argsp_outputs = get_params()

        self.FOLDER_NAME = ".speedupy"
        self.CACHE_FOLDER_NAME = os.path.join(self.FOLDER_NAME, "cache")
        self.BD_PATH = os.path.join(self.FOLDER_NAME, "speedupy.db")        
        self.EXP_FUNCTIONS_FILENAME = os.path.join(self.FOLDER_NAME, 'functions_speedupy.json')
        self.EXP_SERIALIZED_FILENAME = os.path.join(self.FOLDER_NAME, 'experiment_speedupy.pickle')
        
        self.__CONEXAO_BANCO = None
        self.DATA_DICTIONARY = {}
        self.NEW_DATA_DICTIONARY = {}
        self.FUNCTIONS_ALREADY_SELECTED_FROM_DB = []
        self.CACHED_DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()
        self.METADATA = {}
        self.DONT_CACHE_FUNCTION_CALLS = []
        self.NEW_DONT_CACHE_FUNCTION_CALLS = []
        self.SIMULATED_FUNCTION_CALLS = {}
        self.NEW_SIMULATED_FUNCTION_CALLS = {}
        self.FUNCTION_CALLS_PROV = {}
        self.NEW_FUNCTION_CALLS_PROV = {}

        self.FUNCTIONS_2_HASHES = {}

        self.NUM_EXEC_MIN_PARA_INFERENCIA = 20
        self.MAX_ERROR_RATE = 0.2
        self.MIN_TIME_TO_CACHE = 1
        self.MIN_TIME_TO_SIMULATE_FUNC_CALL = 10

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
