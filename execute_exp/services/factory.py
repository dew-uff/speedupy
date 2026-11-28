from typing import Optional

from execute_exp.services.execution_modes.AbstractExecutionMode import (
    AbstractExecutionMode,
)
from execute_exp.services.hashes.Hash import Hash
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import (
    AbstractRetrievalStrategy,
)
from execute_exp.services.revalidations.AbstractRevalidation import AbstractRevalidation
from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.storages.Storage import Storage
from execute_exp.SpeeduPySettings import SpeeduPySettings


def init_mem_arch() -> AbstractMemArch:
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

    retrieval_strategy = _init_retrieval_strategy()
    use_threads = SpeeduPySettings().retrieval_exec_mode == ["thread"]
    if SpeeduPySettings().mem_arch == ["0-dict"]:
        return ZeroDictMemArch(retrieval_strategy, use_threads)
    elif SpeeduPySettings().mem_arch == ["1-dict"]:
        return OneDictMemArch(retrieval_strategy, use_threads)
    elif SpeeduPySettings().mem_arch == ["2-dict"]:
        return OneDictOldDataOneDictNewDataMemArch(retrieval_strategy, use_threads)
    elif SpeeduPySettings().mem_arch == ["2-dict-fast"]:
        return OneDictAllDataOneDictNewDataMemArch(retrieval_strategy, use_threads)
    elif SpeeduPySettings().mem_arch == ["memcached-wt"]:
        return MemcachedWriteThroughMemArch(retrieval_strategy, use_threads)
    elif SpeeduPySettings().mem_arch == ["memcached-wb"]:
        return MemcachedWriteBackMemArch(retrieval_strategy, use_threads)


def _init_retrieval_strategy() -> AbstractRetrievalStrategy:
    from execute_exp.services.retrieval_strategies.EagerRetrieval import EagerRetrieval
    from execute_exp.services.retrieval_strategies.FunctionRetrieval import (
        FunctionRetrieval,
    )
    from execute_exp.services.retrieval_strategies.LazyRetrieval import LazyRetrieval

    storage = _init_storage()
    if SpeeduPySettings().retrieval_strategy == ["lazy"]:
        return LazyRetrieval(storage)
    elif SpeeduPySettings().retrieval_strategy == ["function"]:
        return FunctionRetrieval(storage)
    elif SpeeduPySettings().retrieval_strategy == ["eager"]:
        return EagerRetrieval(storage)


def _init_storage() -> Storage:
    # Each storage module is imported only when its storage is selected, so a
    # driver that is not installed matters only to the storage that needs it.
    serializer = get_serializer()
    if SpeeduPySettings().storage == ["sqlite"]:
        from execute_exp.services.storages.SQLiteStorage import SQLiteStorage

        return SQLiteStorage(serializer)
    elif SpeeduPySettings().storage == ["redis"]:
        from execute_exp.services.storages.RedisStorage import RedisStorage

        return RedisStorage(serializer)
    elif SpeeduPySettings().storage == ["mongo"]:
        from execute_exp.services.storages.MongoStorage import MongoStorage

        return MongoStorage(serializer)
    elif SpeeduPySettings().storage == ["gridfs"]:
        from execute_exp.services.storages.GridFSStorage import GridFSStorage

        return GridFSStorage(serializer)
    elif SpeeduPySettings().storage == ["mongo-file"]:
        from execute_exp.services.storages.FileSystemStorage import FileSystemStorage
        from execute_exp.services.storages.MongoStorage import MongoStorage
        from execute_exp.services.storages.MongoWithFileSystemStorage import (
            MongoWithFileSystemStorage,
        )

        return MongoWithFileSystemStorage(
            MongoStorage(serializer), FileSystemStorage(serializer)
        )
    elif SpeeduPySettings().storage == ["mongo-gridfs"]:
        from execute_exp.services.storages.GridFSStorage import GridFSStorage
        from execute_exp.services.storages.MongoStorage import MongoStorage
        from execute_exp.services.storages.MongoWithGridFSStorage import (
            MongoWithGridFSStorage,
        )

        return MongoWithGridFSStorage(
            MongoStorage(serializer), GridFSStorage(serializer)
        )
    elif SpeeduPySettings().storage == ["file"]:
        from execute_exp.services.storages.FileSystemStorage import FileSystemStorage

        return FileSystemStorage(serializer)
    elif SpeeduPySettings().storage == ["mysql"]:
        from execute_exp.services.storages.MySQLStorage import MySQLStorage

        return MySQLStorage(serializer)


def get_serializer() -> Serializer:
    from execute_exp.services.serializers.CloudpickleSerializer import (
        CloudpickleSerializer,
    )
    from execute_exp.services.serializers.PickleSerializer import PickleSerializer

    if SpeeduPySettings().serializer == ["pickle"]:
        return PickleSerializer()
    elif SpeeduPySettings().serializer == ["cloudpickle"]:
        return CloudpickleSerializer()


def init_exec_mode() -> Optional[AbstractExecutionMode]:
    from execute_exp.services.execution_modes.AccurateMode import AccurateMode
    from execute_exp.services.execution_modes.ProbabilisticCountingMode import (
        ProbabilisticCountingMode,
    )
    from execute_exp.services.execution_modes.ProbabilisticErrorMode import (
        ProbabilisticErrorMode,
    )

    serializer = get_serializer()
    if SpeeduPySettings().exec_mode == ["accurate"]:
        return AccurateMode(serializer, SpeeduPySettings().min_num_exec)
    elif SpeeduPySettings().exec_mode == ["probabilistic-counting"]:
        return ProbabilisticCountingMode(
            serializer,
            SpeeduPySettings().min_num_exec,
            SpeeduPySettings().min_mode_occurrence,
        )
    elif SpeeduPySettings().exec_mode == ["probabilistic-error"]:
        return ProbabilisticErrorMode(
            serializer,
            SpeeduPySettings().min_num_exec,
            SpeeduPySettings().max_error_per_function,
            SpeeduPySettings().confidence_lv,
        )


def init_revalidation(
    exec_mode: Optional[AbstractExecutionMode],
) -> Optional[AbstractRevalidation]:
    from execute_exp.services.revalidations.AdaptativeRevalidation import (
        AdaptativeRevalidation,
    )
    from execute_exp.services.revalidations.FixedRevalidation import FixedRevalidation
    from execute_exp.services.revalidations.NoRevalidation import NoRevalidation

    if exec_mode is None:
        return
    if SpeeduPySettings().revalidation == ["none"]:
        return NoRevalidation()
    elif SpeeduPySettings().revalidation == ["fixed"]:
        return FixedRevalidation(SpeeduPySettings().max_num_exec_til_reval)
    elif SpeeduPySettings().revalidation == ["adaptative"]:
        return AdaptativeRevalidation(
            exec_mode,
            SpeeduPySettings().max_num_exec_til_reval,
            SpeeduPySettings().reduction_factor,
        )


def get_hash() -> Hash:
    from execute_exp.services.hashes.MD5Hash import MD5Hash
    from execute_exp.services.hashes.XXHashHash import XXHashHash

    serializer = get_serializer()
    if SpeeduPySettings().hash == ["md5"]:
        return MD5Hash(serializer)
    elif SpeeduPySettings().hash == ["xxhash"]:
        return XXHashHash(serializer)
    elif SpeeduPySettings().hash == ["museair"]:
        from execute_exp.services.hashes.MuseairBFastHash import MuseairBFastHash

        return MuseairBFastHash(serializer)
    elif SpeeduPySettings().hash == ["a5hash"]:
        from execute_exp.services.hashes.A5Hash import A5Hash

        return A5Hash(serializer)
