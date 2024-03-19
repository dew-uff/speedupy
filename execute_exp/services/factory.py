from typing import Optional
from constantes import Constantes
from execute_exp.services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from execute_exp.services.revalidations.AbstractRevalidation import AbstractRevalidation
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from execute_exp.services.retrieval_strategies.AbstractRetrievalStrategy import AbstractRetrievalStrategy
from execute_exp.services.storages.Storage import Storage
from execute_exp.SpeeduPySettings import SpeeduPySettings

def init_mem_arch() -> AbstractMemArch:
    from execute_exp.services.memory_architecures.ZeroDictMemArch import ZeroDictMemArch
    from execute_exp.services.memory_architecures.OneDictMemArch import OneDictMemArch
    from execute_exp.services.memory_architecures.OneDictOldDataOneDictNewDataMemArch import OneDictOldDataOneDictNewDataMemArch
    from execute_exp.services.memory_architecures.OneDictAllDataOneDictNewDataMemArch import OneDictAllDataOneDictNewDataMemArch

    retrieval_strategy = _init_retrieval_strategy()
    use_threads = SpeeduPySettings().retrieval_exec_mode == ['thread']
    if SpeeduPySettings().num_dict == ['0']:
        return ZeroDictMemArch(retrieval_strategy, use_threads)
    elif SpeeduPySettings().num_dict == ['1']:
        return OneDictMemArch(retrieval_strategy, use_threads)
    elif SpeeduPySettings().num_dict == ['2']:
        return OneDictOldDataOneDictNewDataMemArch(retrieval_strategy, use_threads)
    elif SpeeduPySettings().num_dict == ['2-fast']:
        return OneDictAllDataOneDictNewDataMemArch(retrieval_strategy, use_threads)

def _init_retrieval_strategy() -> AbstractRetrievalStrategy:
    from execute_exp.services.retrieval_strategies.LazyRetrieval import LazyRetrieval
    from execute_exp.services.retrieval_strategies.FunctionRetrieval import FunctionRetrieval
    from execute_exp.services.retrieval_strategies.EagerRetrieval import EagerRetrieval

    storage = _init_storage()
    if SpeeduPySettings().retrieval_strategy == ['lazy']:
        return LazyRetrieval(storage)
    elif SpeeduPySettings().retrieval_strategy == ['function']:
        return FunctionRetrieval(storage)
    elif SpeeduPySettings().retrieval_strategy == ['eager']:
        return EagerRetrieval(storage)

def _init_storage() -> Storage:
    from execute_exp.services.storages.DBStorage import DBStorage
    from execute_exp.services.storages.FileSystemStorage import FileSystemStorage

    if SpeeduPySettings().storage == ['db']: return DBStorage(Constantes().BD_PATH)
    elif SpeeduPySettings().storage == ['file']: return FileSystemStorage(Constantes().CACHE_FOLDER_NAME)
    
def init_exec_mode() -> Optional[AbstractExecutionMode]:
    from execute_exp.services.execution_modes.AccurateMode import AccurateMode
    from execute_exp.services.execution_modes.ProbabilisticCountingMode import ProbabilisticCountingMode
    from execute_exp.services.execution_modes.ProbabilisticErrorMode import ProbabilisticErrorMode

    if SpeeduPySettings().exec_mode == ['accurate']:
        return AccurateMode(SpeeduPySettings().min_num_exec)
    elif SpeeduPySettings().exec_mode == ['probabilistic'] and \
         SpeeduPySettings().strategy == ['counting']:
        return ProbabilisticCountingMode(SpeeduPySettings().min_num_exec, 
                                         SpeeduPySettings().min_mode_occurrence)
    elif SpeeduPySettings().exec_mode == ['probabilistic'] and \
         SpeeduPySettings().strategy == ['error']:
        return ProbabilisticErrorMode(SpeeduPySettings().min_num_exec, 
                                      SpeeduPySettings().max_error_per_function,
                                      SpeeduPySettings().confidence_lv)

def init_revalidation(exec_mode:Optional[AbstractExecutionMode]) -> Optional[AbstractRevalidation]:
    from execute_exp.services.revalidations.NoRevalidation import NoRevalidation
    from execute_exp.services.revalidations.FixedRevalidation import FixedRevalidation
    from execute_exp.services.revalidations.AdaptativeRevalidation import AdaptativeRevalidation
    
    if exec_mode is None: return
    if SpeeduPySettings().revalidation == ['none']:
        return NoRevalidation()
    elif SpeeduPySettings().revalidation == ['fixed']:
        return FixedRevalidation(SpeeduPySettings().max_num_exec_til_reval)
    elif SpeeduPySettings().revalidation == ['adaptative']:
        return AdaptativeRevalidation(exec_mode,
                                      SpeeduPySettings().max_num_exec_til_reval,
                                      SpeeduPySettings().reduction_factor)
