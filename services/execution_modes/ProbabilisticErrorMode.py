from services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from services.execution_modes.util import function_outputs_dict_2_array
from data_access import get_func_call_prov
from constantes import Constantes
import scipy.stats as st
from math import isnan

class ProbabilisticErrorMode(AbstractExecutionMode):
    def func_call_can_be_cached(self, func_call_hash:str) -> bool:
        if Constantes().g_argsp_max_error_per_function is None: return True
        self.__func_call_prov = get_func_call_prov(func_call_hash)
        if self.__func_call_prov.confidence_lv is None or \
           self.__func_call_prov.confidence_lv != Constantes().g_argsp_confidence_level:
            self._set_necessary_helpers()
        return self.__func_call_prov.confidence_error <= Constantes().g_argsp_max_error_per_function

    #Implemented according to https://www.geeksforgeeks.org/how-to-calculate-confidence-intervals-in-python/
    def _set_necessary_helpers(self) -> None:
        data = function_outputs_dict_2_array(self.__func_call_prov.outputs)
        self.__func_call_prov.mean_output = st.tmean(data)
        self.__func_call_prov.confidence_lv = Constantes().g_argsp_confidence_level
        scale = st.sem(data)
        if self.__func_call_prov.total_num_exec <= 30:
            interval = st.t.interval(self.__func_call_prov.confidence_lv,
                                     self.__func_call_prov.total_num_exec-1, 
                                     loc=self.__func_call_prov.mean_output,
                                     scale=scale)
        else:
            interval = st.norm.interval(self.__func_call_prov.confidence_lv,
                                        loc=self.__func_call_prov.mean_output, 
                                        scale=scale)
        self.__func_call_prov.confidence_low_limit = interval[0]
        self.__func_call_prov.confidence_up_limit = interval[1]
        self.__func_call_prov.confidence_error = self.__func_call_prov.confidence_up_limit - self.__func_call_prov.mean_output
        if isnan(self.__func_call_prov.confidence_low_limit) and \
           isnan(self.__func_call_prov.confidence_up_limit) and \
           isnan(self.__func_call_prov.confidence_error):
            self.__func_call_prov.confidence_low_limit = self.__func_call_prov.mean_output
            self.__func_call_prov.confidence_up_limit = self.__func_call_prov.mean_output
            self.__func_call_prov.confidence_error = 0

    def get_func_call_cache(self, func_call_hash:str):
        self.__func_call_prov = get_func_call_prov(func_call_hash)
        if self.__func_call_prov.mean_output is None:
            data = function_outputs_dict_2_array(self.__func_call_prov.outputs)
            self.__func_call_prov.mean_output = st.tmean(data)
        return self.__func_call_prov.mean_output
