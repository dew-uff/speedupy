import os
import threading

from banco import Banco
from SingletonMeta import SingletonMeta
from execute_exp.SpeeduPySettings import SpeeduPySettings

class Constantes(metaclass=SingletonMeta):
    def __init__(self):
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
        if SpeeduPySettings().g_argsp_m != ['v01x'] and self.__CONEXAO_BANCO is None:
            try:
                self.__CONEXAO_BANCO = Banco(self.BD_PATH)
            except: #Need for unit testing!
                self.__CONEXAO_BANCO = None
        return self.__CONEXAO_BANCO

    @CONEXAO_BANCO.setter
    def CONEXAO_BANCO(self, CONEXAO_BANCO):
        self.__CONEXAO_BANCO = CONEXAO_BANCO
