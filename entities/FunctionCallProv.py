class FunctionCallProv():
    def __init__(self, function_call_hash, outputs={}, total_num_exec=0, next_revalidation=None, next_index_weighted_seq=0, mode_rel_freq=None, mode_output=None, weighted_output_seq=None, mean_output=None, confidence_lv=None, confidence_low_limit=None, confidence_up_limit=None, confidence_error=None):
        self.__function_call_hash = function_call_hash
        self.__outputs = outputs
        self.__total_num_exec = total_num_exec
        self.__next_revalidation = next_revalidation
        self.__next_index_weighted_seq = next_index_weighted_seq
        self.__mode_rel_freq = mode_rel_freq
        self.__mode_output = mode_output
        self.__weighted_output_seq = weighted_output_seq
        self.__mean_output = mean_output
        self.__confidence_lv = confidence_lv
        self.__confidence_low_limit = confidence_low_limit
        self.__confidence_up_limit = confidence_up_limit
        self.__confidence_error = confidence_error

    @property
    def function_call_hash(self):
        return self.__function_call_hash

    @property
    def outputs(self):
        return self.__outputs

    @property
    def total_num_exec(self):
        return self.__total_num_exec

    @total_num_exec.setter
    def total_num_exec(self, total_num_exec):
        self.__total_num_exec = total_num_exec

    @property
    def next_revalidation(self):
        return self.__next_revalidation

    @next_revalidation.setter
    def next_revalidation(self, next_revalidation):
        self.__next_revalidation = next_revalidation

    @property
    def next_index_weighted_seq(self):
        return self.__next_index_weighted_seq

    @next_index_weighted_seq.setter
    def next_index_weighted_seq(self, next_index_weighted_seq):
        self.__next_index_weighted_seq = next_index_weighted_seq

    @property
    def mode_rel_freq(self):
        return self.__mode_rel_freq

    @mode_rel_freq.setter
    def mode_rel_freq(self, mode_rel_freq):
        self.__mode_rel_freq = mode_rel_freq

    @property
    def mode_output(self):
        return self.__mode_output

    @mode_output.setter
    def mode_output(self, mode_output):
        self.__mode_output = mode_output

    @property
    def weighted_output_seq(self):
        return self.__weighted_output_seq

    @weighted_output_seq.setter
    def weighted_output_seq(self, weighted_output_seq):
        self.__weighted_output_seq = weighted_output_seq

    @property
    def mean_output(self):
        return self.__mean_output

    @mean_output.setter
    def mean_output(self, mean_output):
        self.__mean_output = mean_output

    @property
    def confidence_lv(self):
        return self.__confidence_lv

    @confidence_lv.setter
    def confidence_lv(self, confidence_lv):
        self.__confidence_lv = confidence_lv

    @property
    def confidence_low_limit(self):
        return self.__confidence_low_limit

    @confidence_low_limit.setter
    def confidence_low_limit(self, confidence_low_limit):
        self.__confidence_low_limit = confidence_low_limit

    @property
    def confidence_up_limit(self):
        return self.__confidence_up_limit

    @confidence_up_limit.setter
    def confidence_up_limit(self, confidence_up_limit):
        self.__confidence_up_limit = confidence_up_limit

    @property
    def confidence_error(self):
        return self.__confidence_error

    @confidence_error.setter
    def confidence_error(self, confidence_error):
        self.__confidence_error = confidence_error