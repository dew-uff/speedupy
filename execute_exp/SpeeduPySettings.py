from SingletonMeta import SingletonMeta
from execute_exp.parser_params import get_params


class SpeeduPySettings(metaclass=SingletonMeta):
    def __init__(self):
        self.mem_arch, \
            self.retrieval_strategy, \
            self.retrieval_exec_mode, \
            self.hash, \
            self.storage, \
            self.serializer, \
            self.min_exec_time_to_memoize, \
            self.measure_time, \
            self.profile, \
            self.exec_mode, \
            self.revalidation, \
            self.max_num_exec_til_reval, \
            self.reduction_factor, \
            self.min_num_exec, \
            self.min_mode_occurrence, \
            self.confidence_lv, \
            self.max_error_per_function = get_params()
