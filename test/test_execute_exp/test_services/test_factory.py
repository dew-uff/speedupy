from unittest.mock import patch

import pytest

from execute_exp.services.execution_modes.AccurateMode import AccurateMode
from execute_exp.services.execution_modes.ProbabilisticCountingMode import (
    ProbabilisticCountingMode,
)
from execute_exp.services.execution_modes.ProbabilisticErrorMode import (
    ProbabilisticErrorMode,
)
from execute_exp.services.factory import (
    get_hash,
    get_serializer,
    init_exec_mode,
    init_mem_arch,
    init_revalidation,
)
from execute_exp.services.hashes.A5Hash import A5Hash
from execute_exp.services.hashes.MD5Hash import MD5Hash
from execute_exp.services.hashes.MeowHash import MeowHash
from execute_exp.services.hashes.MurmurHash import MurmurHash
from execute_exp.services.hashes.MuseairBFastHash import MuseairBFastHash
from execute_exp.services.hashes.XXHashHash import XXHashHash
from execute_exp.services.memory_architecures.MemcachedWriteBackMemArch import (
    MemcachedWriteBackMemArch,
)
from execute_exp.services.memory_architecures.MemcachedWriteThroughMemArch import (
    MemcachedWriteThroughMemArch,
)
from execute_exp.services.memory_architecures.OneDictAllDataOneDictNewDataMemArch import (
    OneDictAllDataOneDictNewDataMemArch,
)
from execute_exp.services.memory_architecures.OneDictMemArch import OneDictMemArch
from execute_exp.services.memory_architecures.OneDictOldDataOneDictNewDataMemArch import (
    OneDictOldDataOneDictNewDataMemArch,
)
from execute_exp.services.memory_architecures.ZeroDictMemArch import ZeroDictMemArch
from execute_exp.services.retrieval_strategies.EagerRetrieval import EagerRetrieval
from execute_exp.services.retrieval_strategies.FunctionRetrieval import (
    FunctionRetrieval,
)
from execute_exp.services.retrieval_strategies.LazyRetrieval import LazyRetrieval
from execute_exp.services.revalidations.AdaptativeRevalidation import (
    AdaptativeRevalidation,
)
from execute_exp.services.revalidations.FixedRevalidation import FixedRevalidation
from execute_exp.services.revalidations.NoRevalidation import NoRevalidation
from execute_exp.services.serializers.CloudpickleSerializer import CloudpickleSerializer
from execute_exp.services.serializers.PickleSerializer import PickleSerializer
from execute_exp.services.storages.FileSystemStorage import FileSystemStorage
from execute_exp.services.storages.GridFSStorage import GridFSStorage
from execute_exp.services.storages.MongoStorage import MongoStorage
from execute_exp.services.storages.MongoWithFileSystemStorage import (
    MongoWithFileSystemStorage,
)
from execute_exp.services.storages.MongoWithGridFSStorage import MongoWithGridFSStorage
from execute_exp.services.storages.RedisStorage import RedisStorage
from execute_exp.services.storages.SQLiteStorage import SQLiteStorage

MEM_ARCHS = [
    ("0-dict", ZeroDictMemArch),
    ("1-dict", OneDictMemArch),
    ("2-dict", OneDictOldDataOneDictNewDataMemArch),
    ("2-dict-fast", OneDictAllDataOneDictNewDataMemArch),
    pytest.param(
        "memcached-wt", MemcachedWriteThroughMemArch, marks=pytest.mark.memcached
    ),
    pytest.param(
        "memcached-wb", MemcachedWriteBackMemArch, marks=pytest.mark.memcached
    ),
]
RETRIEVAL_STRATEGIES = [
    ("lazy", LazyRetrieval),
    ("function", FunctionRetrieval),
    ("eager", EagerRetrieval),
]
STORAGES = [
    ("sqlite", SQLiteStorage),
    pytest.param("redis", RedisStorage, marks=pytest.mark.redis),
    pytest.param("mongo", MongoStorage, marks=pytest.mark.mongo),
    pytest.param("gridfs", GridFSStorage, marks=pytest.mark.mongo),
    pytest.param("mongo-file", MongoWithFileSystemStorage, marks=pytest.mark.mongo),
    pytest.param("mongo-gridfs", MongoWithGridFSStorage, marks=pytest.mark.mongo),
    ("file", FileSystemStorage),
]
SERIALIZERS = [("pickle", PickleSerializer), ("cloudpickle", CloudpickleSerializer)]
HASHES = [
    ("md5", MD5Hash),
    ("murmur", MurmurHash),
    ("xxhash", XXHashHash),
    pytest.param("meowhash", MeowHash, marks=pytest.mark.native("meow")),
    pytest.param("museair", MuseairBFastHash, marks=pytest.mark.native("museair")),
    pytest.param("a5hash", A5Hash, marks=pytest.mark.native("a5hash")),
]
EXEC_MODES = [
    ("no-cache", None),
    ("manual", None),
    ("accurate", AccurateMode),
    ("probabilistic-counting", ProbabilisticCountingMode),
    ("probabilistic-error", ProbabilisticErrorMode),
]
REVALIDATIONS = [
    ("none", NoRevalidation),
    ("fixed", FixedRevalidation),
    ("adaptative", AdaptativeRevalidation),
]


@pytest.fixture
def settings(tmp_path, monkeypatch):
    """The settings with one fixed value per option; a test changes the one it covers.

    The SQLite storage opens its database in ``.speedupy/`` of the current
    directory, so the test runs in a directory that has one.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".speedupy").mkdir()
    with patch("execute_exp.services.factory.SpeeduPySettings") as SpeeduPySettings:
        settings = SpeeduPySettings()
        settings.mem_arch = ["0-dict"]
        settings.retrieval_exec_mode = ["sequential"]
        settings.retrieval_strategy = ["lazy"]
        settings.storage = ["file"]
        settings.serializer = ["pickle"]
        settings.hash = ["md5"]
        settings.exec_mode = ["accurate"]
        settings.revalidation = ["none"]
        settings.min_num_exec = 20
        settings.min_mode_occurrence = 0.5
        settings.max_error_per_function = 20
        settings.confidence_lv = 0.9
        settings.max_num_exec_til_reval = 20
        settings.reduction_factor = 0.5
        yield settings


@pytest.mark.parametrize(("name", "mem_arch_class"), MEM_ARCHS)
def test_init_mem_arch_builds_each_memory_architecture(settings, name, mem_arch_class):
    settings.mem_arch = [name]
    assert isinstance(init_mem_arch(), mem_arch_class)


@pytest.mark.parametrize(("name", "retrieval_class"), RETRIEVAL_STRATEGIES)
def test_init_mem_arch_builds_each_retrieval_strategy(settings, name, retrieval_class):
    settings.retrieval_strategy = [name]
    assert isinstance(init_mem_arch()._retrieval_strategy, retrieval_class)


@pytest.mark.parametrize(("name", "storage_class"), STORAGES)
def test_init_mem_arch_builds_each_storage(settings, name, storage_class):
    settings.storage = [name]
    assert isinstance(init_mem_arch()._retrieval_strategy._storage, storage_class)


@pytest.mark.parametrize(("name", "serializer_class"), SERIALIZERS)
def test_init_mem_arch_builds_each_serializer(settings, name, serializer_class):
    settings.serializer = [name]
    storage = init_mem_arch()._retrieval_strategy._storage
    assert isinstance(storage._serializer, serializer_class)


@pytest.mark.parametrize(
    ("mode", "use_threads"), [("sequential", False), ("thread", True)]
)
def test_init_mem_arch_follows_the_retrieval_exec_mode(settings, mode, use_threads):
    settings.retrieval_exec_mode = [mode]
    assert init_mem_arch()._use_threads is use_threads


@pytest.mark.parametrize(("name", "serializer_class"), SERIALIZERS)
def test_get_serializer(settings, name, serializer_class):
    settings.serializer = [name]
    assert isinstance(get_serializer(), serializer_class)


@pytest.mark.parametrize(("name", "exec_mode_class"), EXEC_MODES)
def test_init_exec_mode(settings, name, exec_mode_class):
    settings.exec_mode = [name]

    result = init_exec_mode()

    if exec_mode_class is None:
        assert result is None
        return
    assert isinstance(result, exec_mode_class)
    assert isinstance(result._serializer, PickleSerializer)
    assert result._min_num_exec == settings.min_num_exec
    if exec_mode_class is ProbabilisticCountingMode:
        assert result._min_mode_occurrence == settings.min_mode_occurrence
    elif exec_mode_class is ProbabilisticErrorMode:
        assert result._max_error_per_function == settings.max_error_per_function
        assert result._confidence_lv == settings.confidence_lv


@pytest.mark.parametrize(("name", "revalidation_class"), REVALIDATIONS)
def test_init_revalidation(settings, name, revalidation_class):
    settings.revalidation = [name]

    result = init_revalidation(AccurateMode)

    assert isinstance(result, revalidation_class)
    if revalidation_class is FixedRevalidation:
        assert (
            result._FixedRevalidation__fixed_num_exec_til_reval
            == settings.max_num_exec_til_reval
        )
    elif revalidation_class is AdaptativeRevalidation:
        assert (
            result._AdaptativeRevalidation__current_num_exec_til_reval
            == settings.max_num_exec_til_reval
        )
        assert (
            result._AdaptativeRevalidation__adaptative_factor
            == settings.reduction_factor
        )


def test_init_revalidation_is_none_without_an_exec_mode(settings):
    assert init_revalidation(None) is None


@pytest.mark.parametrize(("name", "hash_class"), HASHES)
def test_get_hash(settings, name, hash_class):
    settings.hash = [name]

    result = get_hash()

    assert isinstance(result, hash_class)
    assert isinstance(result._serializer, PickleSerializer)
