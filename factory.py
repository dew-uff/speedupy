from execute_exp.services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from execute_exp.services.storages.Storage import Storage
from execute_exp.SpeeduPySettings import SpeeduPySettings

#TODO:TEST
def init_exec_mode():
    from execute_exp.services.execution_modes.AccurateMode import AccurateMode
    from execute_exp.services.execution_modes.ProbabilisticCountingMode import ProbabilisticCountingMode
    from execute_exp.services.execution_modes.ProbabilisticErrorMode import ProbabilisticErrorMode

    if SpeeduPySettings().g_argsp_exec_mode == ['accurate']:
        return AccurateMode()
    elif SpeeduPySettings().g_argsp_exec_mode == ['probabilistic'] and \
         SpeeduPySettings().g_argsp_strategy == ['counting']:
        return ProbabilisticCountingMode()
    elif SpeeduPySettings().g_argsp_exec_mode == ['probabilistic'] and \
         SpeeduPySettings().g_argsp_strategy == ['error']:
        return ProbabilisticErrorMode()

#TODO:TEST
def init_revalidation(exec_mode:AbstractExecutionMode):
    from execute_exp.services.revalidations.NoRevalidation import NoRevalidation
    from execute_exp.services.revalidations.FixedRevalidation import FixedRevalidation
    from execute_exp.services.revalidations.AdaptativeRevalidation import AdaptativeRevalidation

    if SpeeduPySettings().g_argsp_revalidation == ['none']:
        return NoRevalidation()
    elif SpeeduPySettings().g_argsp_revalidation == ['fixed']:
        return FixedRevalidation(SpeeduPySettings().g_argsp_max_num_exec_til_revalidation)
    elif SpeeduPySettings().g_argsp_revalidation == ['adaptative']:
        return AdaptativeRevalidation(exec_mode,
                                      SpeeduPySettings().g_argsp_max_num_exec_til_revalidation, SpeeduPySettings().g_argsp_reduction_factor)

#TODO:TEST
def init_storage():
    from execute_exp.services.storages.DBStorage import DBStorage
    from execute_exp.services.storages.FileSystemStorage import FileSystemStorage

    if SpeeduPySettings().g_argsp_s == ['db']: return DBStorage()
    elif SpeeduPySettings().g_argsp_s == ['file']: return FileSystemStorage()

#TODO:TEST
def init_mem_arch(storage:Storage):
    from execute_exp.memory_architectures.V01MemArch import V01MemArch
    from execute_exp.memory_architectures.V021MemArch import V021MemArch
    from execute_exp.memory_architectures.V022MemArch import V022MemArch
    from execute_exp.memory_architectures.V023MemArch import V023MemArch
    from execute_exp.memory_architectures.V024MemArch import V024MemArch
    from execute_exp.memory_architectures.V025MemArch import V025MemArch
    from execute_exp.memory_architectures.V026MemArch import V026MemArch
    from execute_exp.memory_architectures.V027MemArch import V027MemArch

    if SpeeduPySettings().g_argsp_m == ['ad']: return V01MemArch(storage)
    elif SpeeduPySettings().g_argsp_m == ['1d-ow']: return V021MemArch(storage)
    elif SpeeduPySettings().g_argsp_m == ['1d-ad']: return V022MemArch(storage)
    elif SpeeduPySettings().g_argsp_m == ['2d-ad']: return V023MemArch(storage)
    elif SpeeduPySettings().g_argsp_m == ['2d-ad-t']: return V024MemArch(storage)
    elif SpeeduPySettings().g_argsp_m == ['2d-ad-f']: return V025MemArch(storage)
    elif SpeeduPySettings().g_argsp_m == ['2d-ad-ft']: return V026MemArch(storage)
    elif SpeeduPySettings().g_argsp_m == ['2d-lz']: return V027MemArch(storage)
