import sys
from SingletonMeta import SingletonMeta
from execute_exp.parser_params import get_params

class SpeeduPySettings(metaclass=SingletonMeta):
    def __init__(self):
        self.num_dict, \
        self.retrieval_strategy, \
        self.retrieval_exec_mode, \
        self.g_argsp_hash, \
        self.storage, \
        self.exec_mode, \
        self.strategy, \
        self.revalidation, \
        self.max_num_exec_til_reval, \
        self.reduction_factor, \
        self.g_argsp_min_num_exec, \
        self.min_mode_occurrence, \
        self.confidence_lv, \
        self.max_error_per_function = get_params()

        self._validate_user_args()

    def _validate_user_args(self):
        if self._exec_mode_unset():
            self._set_default_exec_mode()
        elif self._probabilistic_mode_without_strategy():
            self._set_default_strategy()

    def _exec_mode_unset(self):
        return self.exec_mode is None

    def _set_default_exec_mode(self):
        self.exec_mode = 'probabilistic' if self.strategy else 'manual'

    def _probabilistic_mode_without_strategy(self):
        return self.exec_mode == 'probabilistic' and self.strategy is None

    def _set_default_strategy(self):
        self.strategy = 'error'
