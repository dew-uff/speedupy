from execute_exp.entitites.Metadata import Metadata
from execute_exp.entitites.FunctionCallProv import FunctionCallProv
from execute_exp.services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from execute_exp.services.execution_modes.util import function_outputs_dict_2_array
from execute_exp.services.serializers.Serializer import Serializer
import scipy.stats as st
from math import isnan


class ProbabilisticErrorMode(AbstractExecutionMode):
    def __init__(self, serializer: Serializer, min_num_exec: int, max_error_per_function: float, confidence_lv: float):
        super().__init__(serializer, min_num_exec)
        self._max_error_per_function = max_error_per_function
        self._confidence_lv = confidence_lv

    def func_call_can_be_cached(self, fc_prov: FunctionCallProv) -> bool:
        if self._max_error_per_function is None: return True
        self._fc_prov = fc_prov
        if self._fc_prov.confidence_lv is None or \
           self._fc_prov.confidence_lv != self._confidence_lv:
            self._set_necessary_helpers()
        return self._fc_prov.confidence_error <= self._max_error_per_function

    # Implemented according to https://www.geeksforgeeks.org/how-to-calculate-confidence-intervals-in-python/
    def _set_necessary_helpers(self) -> None:
        data = function_outputs_dict_2_array(self._serializer, self._fc_prov.outputs)
        self._fc_prov.mean_output = st.tmean(data)
        self._fc_prov.confidence_lv = self._confidence_lv
        scale = st.sem(data)
        if self._fc_prov.total_num_exec <= 30:
            interval = st.t.interval(self._fc_prov.confidence_lv,
                                     self._fc_prov.total_num_exec - 1,
                                     loc=self._fc_prov.mean_output,
                                     scale=scale)
        else:
            interval = st.norm.interval(self._fc_prov.confidence_lv,
                                        loc=self._fc_prov.mean_output,
                                        scale=scale)
        self._fc_prov.confidence_low_limit = interval[0]
        self._fc_prov.confidence_up_limit = interval[1]
        self._fc_prov.confidence_error = self._fc_prov.confidence_up_limit - self._fc_prov.mean_output
        if isnan(self._fc_prov.confidence_low_limit) and \
           isnan(self._fc_prov.confidence_up_limit) and \
           isnan(self._fc_prov.confidence_error):
            self._fc_prov.confidence_low_limit = self._fc_prov.mean_output
            self._fc_prov.confidence_up_limit = self._fc_prov.mean_output
            self._fc_prov.confidence_error = 0

    def get_func_call_cache(self, fc_prov: FunctionCallProv):
        if fc_prov.mean_output is None:
            data = function_outputs_dict_2_array(self._serializer, fc_prov.outputs)
            fc_prov.mean_output = st.tmean(data)
        return fc_prov.mean_output

    def func_call_acted_as_expected(self, fc_prov: FunctionCallProv, metadata: Metadata):
        low_limit = fc_prov.mean_output - fc_prov.confidence_error / 2
        up_limit = fc_prov.mean_output + fc_prov.confidence_error / 2
        return low_limit <= metadata.return_value and metadata.return_value <= up_limit
