from typing import Optional
from execute_exp.services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
# from execute_exp.services.revalidations.AbstractRevalidation import AbstractRevalidation
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy
from execute_exp.services.storages.Storage import Storage
from execute_exp.SpeeduPySettings import SpeeduPySettings

#TODO:TEST
def init_mem_arch() -> AbstractMemArch:
    from execute_exp.services.memory_architecures.ZeroDictMemArch import ZeroDictMemArch
    from execute_exp.services.memory_architecures.OneDictMemArch import OneDictMemArch
    from execute_exp.services.memory_architecures.OneDictOldDataOneDictNewDataMemArch import OneDictOldDataOneDictNewDataMemArch
    from execute_exp.services.memory_architecures.OneDictAllDataOneDictNewDataMemArch import OneDictAllDataOneDictNewDataMemArch

    storage = _init_storage()
    retrieval_strategy = _init_retrieval_strategy(storage)
    use_threads = SpeeduPySettings().retrieval_exec_mode == ['thread']
    if SpeeduPySettings().num_dict == ['0']:
        return ZeroDictMemArch(storage, retrieval_strategy, use_threads)
    elif SpeeduPySettings().num_dict == ['1']:
        return OneDictMemArch(storage, retrieval_strategy, use_threads)
    elif SpeeduPySettings().num_dict == ['2']:
        return OneDictOldDataOneDictNewDataMemArch(storage, retrieval_strategy, use_threads)
    elif SpeeduPySettings().num_dict == ['2-fast']:
        return OneDictAllDataOneDictNewDataMemArch(storage, retrieval_strategy, use_threads)

#TODO:TEST
def _init_storage() -> Storage:
    from execute_exp.services.storages.DBStorage import DBStorage
    from execute_exp.services.storages.FileSystemStorage import FileSystemStorage

    if SpeeduPySettings().g_argsp_s == ['db']: return DBStorage()
    elif SpeeduPySettings().g_argsp_s == ['file']: return FileSystemStorage()

#TODO:TEST
def _init_retrieval_strategy(storage:Storage) -> AbstractRetrievalStrategy:
    from execute_exp.services.retrieval_strategies.LazyRetrieval import LazyRetrieval
    from execute_exp.services.retrieval_strategies.FunctionRetrieval import FunctionRetrieval
    from execute_exp.services.retrieval_strategies.EagerRetrieval import EagerRetrieval

    if SpeeduPySettings().retrieval_strategy == ['lazy']:
        return LazyRetrieval(storage)
    elif SpeeduPySettings().retrieval_strategy == ['function']:
        return FunctionRetrieval(storage)
    elif SpeeduPySettings().retrieval_strategy == ['eager']:
        return EagerRetrieval(storage)
    
#TODO:TEST
def init_exec_mode() -> Optional[AbstractExecutionMode]:
    from execute_exp.services.execution_modes.AccurateMode import AccurateMode
    from execute_exp.services.execution_modes.ProbabilisticCountingMode import ProbabilisticCountingMode
    from execute_exp.services.execution_modes.ProbabilisticErrorMode import ProbabilisticErrorMode

    if SpeeduPySettings().exec_mode == ['accurate']:
        return AccurateMode()
    elif SpeeduPySettings().exec_mode == ['probabilistic'] and \
         SpeeduPySettings().strategy == ['counting']:
        return ProbabilisticCountingMode()
    elif SpeeduPySettings().exec_mode == ['probabilistic'] and \
         SpeeduPySettings().strategy == ['error']:
        return ProbabilisticErrorMode()

#TODO:TEST
def init_revalidation(exec_mode:Optional[AbstractExecutionMode]): #-> Optional[AbstractRevalidation]:
    from execute_exp.services.revalidations.NoRevalidation import NoRevalidation
    from execute_exp.services.revalidations.FixedRevalidation import FixedRevalidation
    from execute_exp.services.revalidations.AdaptativeRevalidation import AdaptativeRevalidation
    
    if exec_mode is None: return
    if SpeeduPySettings().g_argsp_revalidation == ['none']:
        return NoRevalidation()
    elif SpeeduPySettings().g_argsp_revalidation == ['fixed']:
        return FixedRevalidation(SpeeduPySettings().g_argsp_max_num_exec_til_revalidation)
    elif SpeeduPySettings().g_argsp_revalidation == ['adaptative']:
        return AdaptativeRevalidation(exec_mode,
                                      SpeeduPySettings().g_argsp_max_num_exec_til_revalidation, SpeeduPySettings().g_argsp_reduction_factor)
