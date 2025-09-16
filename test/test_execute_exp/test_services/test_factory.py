from unittest.mock import patch
import unittest, os, sys

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from entities.BancoSQLite import BancoSQLite
from execute_exp.services.factory import get_serializer, init_revalidation, init_exec_mode, init_mem_arch
from execute_exp.services.serializers.PickleSerializer import PickleSerializer
from execute_exp.services.serializers.CloudpickleSerializer import CloudpickleSerializer
from execute_exp.services.storages.SQLiteStorage import SQLiteStorage
from execute_exp.services.storages.RedisStorage import RedisStorage
from execute_exp.services.storages.MongoStorage import MongoStorage
from execute_exp.services.storages.FileSystemStorage import FileSystemStorage
from execute_exp.services.retrieval_strategies.LazyRetrieval import LazyRetrieval
from execute_exp.services.retrieval_strategies.FunctionRetrieval import FunctionRetrieval
from execute_exp.services.retrieval_strategies.EagerRetrieval import EagerRetrieval
from execute_exp.services.memory_architecures.ZeroDictMemArch import ZeroDictMemArch
from execute_exp.services.memory_architecures.OneDictMemArch import OneDictMemArch
from execute_exp.services.memory_architecures.OneDictOldDataOneDictNewDataMemArch import OneDictOldDataOneDictNewDataMemArch
from execute_exp.services.memory_architecures.OneDictAllDataOneDictNewDataMemArch import OneDictAllDataOneDictNewDataMemArch
from execute_exp.services.execution_modes.AccurateMode import AccurateMode
from execute_exp.services.execution_modes.ProbabilisticCountingMode import ProbabilisticCountingMode
from execute_exp.services.execution_modes.ProbabilisticErrorMode import ProbabilisticErrorMode
from execute_exp.services.revalidations.NoRevalidation import NoRevalidation
from execute_exp.services.revalidations.FixedRevalidation import FixedRevalidation
from execute_exp.services.revalidations.AdaptativeRevalidation import AdaptativeRevalidation
import sys, random


class TestFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.BD_PATH = 'speedupy.db'
        BancoSQLite.nome_banco = cls.BD_PATH

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.BD_PATH):
            os.remove(cls.BD_PATH)

    def set_random_values(self, SpeeduPySettings):
        self.mem_arch = random.choice([['0', ZeroDictMemArch],
                                       ['1', OneDictMemArch],
                                       ['2', OneDictOldDataOneDictNewDataMemArch],
                                       ['2-fast', OneDictAllDataOneDictNewDataMemArch]])
        SpeeduPySettings().num_dict = [self.mem_arch[0]]

        SpeeduPySettings().retrieval_exec_mode = [random.choice(['sequential', 'thread'])]

        self.retrieval_strategy = random.choice([['lazy', LazyRetrieval],
                                                 ['function', FunctionRetrieval],
                                                 ['eager', EagerRetrieval]])
        SpeeduPySettings().retrieval_strategy = [self.retrieval_strategy[0]]

        self.storage = random.choice([['sqlite', SQLiteStorage],
                                      ['redis', RedisStorage],
                                      ['mongo', MongoStorage],
                                      ['file', FileSystemStorage]])
        SpeeduPySettings().storage = [self.storage[0]]

        self.serializer = random.choice([['pickle', PickleSerializer],
                                         ['cloudpickle',  CloudpickleSerializer]])
        SpeeduPySettings().serializer = [self.serializer[0]]

        self.exec_mode = random.choice([['no-cache', None],
                                        ['manual', None],
                                        ['accurate', AccurateMode],
                                        ['probabilistic-counting', ProbabilisticCountingMode],
                                        ['probabilistic-error', ProbabilisticErrorMode]])
        SpeeduPySettings().exec_mode = [self.exec_mode[0]]

        self.revalidation = random.choice([['none', NoRevalidation],
                                           ['fixed', FixedRevalidation],
                                           ['adaptative', AdaptativeRevalidation]])
        SpeeduPySettings().revalidation = [self.revalidation[0]]

        SpeeduPySettings().min_num_exec = random.randint(10, 50)
        SpeeduPySettings().min_mode_occurrence = random.random()
        SpeeduPySettings().max_error_per_function = random.randint(10, 50)
        SpeeduPySettings().confidence_lv = random.random()
        SpeeduPySettings().max_num_exec_til_reval = random.randint(10, 50)
        SpeeduPySettings().reduction_factor = random.random()

    @patch("execute_exp.services.factory.SpeeduPySettings")
    def test_init_mem_arch(self, SpeeduPySettings):
        self.set_random_values(SpeeduPySettings)

        mem_arch = init_mem_arch()
        retrieval_strategy = mem_arch._retrieval_strategy
        storage = retrieval_strategy._storage
        serializer = storage._serializer

        self.assertIsInstance(mem_arch, self.mem_arch[1])
        self.assertIsInstance(retrieval_strategy, self.retrieval_strategy[1])
        self.assertIsInstance(storage, self.storage[1])
        self.assertIsInstance(serializer, self.serializer[1])
        if SpeeduPySettings().retrieval_exec_mode == ['sequential']: self.assertFalse(mem_arch._use_threads)
        if SpeeduPySettings().retrieval_exec_mode == ['thread']: self.assertTrue(mem_arch._use_threads)

    @patch("execute_exp.services.factory.SpeeduPySettings")
    def test_init_exec_mode(self, SpeeduPySettings):
        self.set_random_values(SpeeduPySettings)

        result = init_exec_mode()

        if self.exec_mode[1] is None:
            self.assertIsNone(result)
            return

        self.assertIsInstance(result, self.exec_mode[1])
        self.assertIsInstance(result._serializer, self.serializer[1])
        self.assertEqual(result._min_num_exec, SpeeduPySettings().min_num_exec)

        if self.exec_mode[1] == ProbabilisticCountingMode:
            self.assertEqual(result._ProbabilisticCountingMode__min_mode_occurrence, SpeeduPySettings().min_mode_occurrence)
        elif self.exec_mode[1] == ProbabilisticErrorMode:
            self.assertEqual(result._ProbabilisticErrorMode__max_error_per_function, SpeeduPySettings().max_error_per_function)
            self.assertEqual(result._ProbabilisticErrorMode__confidence_lv, SpeeduPySettings().confidence_lv)

    @patch("execute_exp.services.factory.SpeeduPySettings")
    def test_init_revalidation(self, SpeeduPySettings):
        self.set_random_values(SpeeduPySettings)

        result = init_revalidation(self.exec_mode[1])

        if self.exec_mode[1] is None:
            self.assertIsNone(result)
            return

        self.assertIsInstance(result, self.revalidation[1])
        if self.revalidation[1] == FixedRevalidation:
            self.assertEqual(result._FixedRevalidation__fixed_num_exec_til_reval, SpeeduPySettings().max_num_exec_til_reval)
        elif self.revalidation[1] == AdaptativeRevalidation:
            self.assertEqual(result._AdaptativeRevalidation__current_num_exec_til_reval, SpeeduPySettings().max_num_exec_til_reval)
            self.assertEqual(result._AdaptativeRevalidation__adaptative_factor, SpeeduPySettings().reduction_factor)

    @patch("execute_exp.services.factory.SpeeduPySettings")
    def test_get_serializer(self, SpeeduPySettings):
        self.set_random_values(SpeeduPySettings)
        self.assertIsInstance(get_serializer(), self.serializer[1])


if __name__ == '__main__':
    unittest.main()
