import os
from SingletonMeta import SingletonMeta

class Constantes(metaclass=SingletonMeta):
    def __init__(self):
        self.FOLDER_NAME = ".speedupy"
        self.CACHE_FOLDER_NAME = os.path.join(self.FOLDER_NAME, "cache")
        self.BD_PATH = os.path.join(self.FOLDER_NAME, "speedupy.db")        
        self.EXP_FUNCTIONS_FILENAME = os.path.join(self.FOLDER_NAME, 'functions_speedupy.json')
        self.EXP_SERIALIZED_FILENAME = os.path.join(self.FOLDER_NAME, 'experiment_speedupy.pickle')
