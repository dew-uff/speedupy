import sys
from SingletonMeta import SingletonMeta
from execute_exp.parser_params import get_params

class SpeeduPySettings(metaclass=SingletonMeta):
    def __init__(self):
        self.g_argsp_num_dict, \
        self.g_argsp_retrieval_strategy, \
        self.g_argsp_retrieval_exec_mode, \
        self.g_argsp_hash, \
        self.g_argsp_s, \
        self.g_argsp_exec_mode, \
        self.g_argsp_strategy, \
        self.g_argsp_revalidation, \
        self.g_argsp_max_num_exec_til_revalidation, \
        self.g_argsp_reduction_factor, \
        self.g_argsp_min_num_exec, \
        self.g_argsp_min_mode_occurrence, \
        self.g_argsp_confidence_level, \
        self.g_argsp_max_error_per_function = get_params()

        self._validate_user_args()

    def _validate_user_args(self):
        if self._exec_mode_unset():
            self._set_default_exec_mode()
        elif self._probabilistic_mode_without_strategy():
            self._set_default_strategy()

    def _exec_mode_unset(self):
        return self.g_argsp_exec_mode is None

    def _set_default_exec_mode(self):
        self.g_argsp_exec_mode = 'probabilistic' if self.g_argsp_strategy else 'manual'

    def _probabilistic_mode_without_strategy(self):
        return self.g_argsp_exec_mode == 'probabilistic' and self.g_argsp_strategy is None

    def _set_default_strategy(self):
        self.g_argsp_strategy = 'error'
