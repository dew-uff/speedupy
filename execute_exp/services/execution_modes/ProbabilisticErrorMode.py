from execute_exp.entitites.Metadata import Metadata
from execute_exp.services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from execute_exp.services.execution_modes.util import function_outputs_dict_2_array
from execute_exp.services.DataAccess import DataAccess
import scipy.stats as st
from math import isnan

class ProbabilisticErrorMode(AbstractExecutionMode):
    def __init__(self, min_num_exec, max_error_per_function:float, confidence_lv:float):
        super().__init__(min_num_exec)
        self.__max_error_per_function = max_error_per_function
        self.__confidence_lv = confidence_lv

    def func_call_can_be_cached(self, func_call_hash:str) -> bool:
        if self.__max_error_per_function is None: return True
        self.__func_call_prov = DataAccess().get_function_call_prov_entry(func_call_hash)
        if self.__func_call_prov.confidence_lv is None or \
           self.__func_call_prov.confidence_lv != self.__confidence_lv:
            self._set_necessary_helpers()
        return self.__func_call_prov.confidence_error <= self.__max_error_per_function

    #Implemented according to https://www.geeksforgeeks.org/how-to-calculate-confidence-intervals-in-python/
    def _set_necessary_helpers(self) -> None:
        data = function_outputs_dict_2_array(self.__func_call_prov.outputs)
        self.__func_call_prov.mean_output = st.tmean(data)
        self.__func_call_prov.confidence_lv = self.__confidence_lv
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
        self.__func_call_prov = DataAccess().get_function_call_prov_entry(func_call_hash)
        if self.__func_call_prov.mean_output is None:
            data = function_outputs_dict_2_array(self.__func_call_prov.outputs)
            self.__func_call_prov.mean_output = st.tmean(data)
        return self.__func_call_prov.mean_output

    def func_call_acted_as_expected(self, func_call_hash:str, metadata:Metadata):
        func_call_prov = DataAccess().get_function_call_prov_entry(func_call_hash)
        low_limit = func_call_prov.mean_output - func_call_prov.confidence_error/2
        up_limit = func_call_prov.mean_output + func_call_prov.confidence_error/2
        return low_limit <= metadata.return_value and metadata.return_value <= up_limit
