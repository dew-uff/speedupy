from typing import Dict, Tuple, List

from services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from services.execution_modes.util import func_call_mode_output_occurs_enough
from data_access import get_func_call_prov
from constantes import Constantes
from copy import deepcopy
from math import ceil
import pickle

#TODO: TEST
class ProbabilisticFrequencyMode(AbstractExecutionMode):
    def func_call_can_be_cached(self, func_call_hash:str) -> bool:
        return func_call_mode_output_occurs_enough(func_call_hash,
                                                   Constantes().g_argsp_min_mode_occurrence)

    def get_func_call_cache(self, func_call_hash:str):
        self.__func_call_prov = get_func_call_prov(func_call_hash)
        if self.__func_call_prov.weighted_output_seq is None:
            self._calculate_weighted_output_seq()
        index = self.__func_call_prov.next_index_weighted_seq
        if index + 1 < len(self.__func_call_prov.weighted_output_seq):
            self.__func_call_prov.next_index_weighted_seq += 1
        else:
            self.__func_call_prov.next_index_weighted_seq = 0
        return self.__func_call_prov.weighted_output_seq[index]
    
    def _calculate_weighted_output_seq(self):
        mode_abs_freq = self.__get_mode_abs_freq()
        output_weights = self.__get_function_output_weights_based_on_the_mode_freq(mode_abs_freq)
        begin_seq, num_occurences_outputs_on_seq = self.__get_beginning_of_output_seq_interleaved_with_statistical_mode(mode_abs_freq, output_weights)
        remaining_outputs = self.__get_remaining_outputs_on_weighted_seq(num_occurences_outputs_on_seq)
        end_seq = self.__get_end_of_output_seq_with_interleaved_remaining_outputs(remaining_outputs)
        self.__func_call_prov.weighted_output_seq = begin_seq + end_seq

    def __get_mode_abs_freq(self) -> int:
        for output in self.__func_call_prov.outputs:
            if output['value'] == self.__func_call_prov.mode_output:
                return output['freq']
            
    def __get_function_output_weights_based_on_the_mode_freq(self, mode_abs_freq:int) -> Dict:
        output_weights = {}
        for output in self.__func_call_prov.outputs:
            if output['value'] == self.__func_call_prov.mode_output: continue
            key = pickle.dumps(output['value'])
            output_weights[key] = ceil(mode_abs_freq/output['freq'])
        return output_weights
    
    def __get_beginning_of_output_seq_interleaved_with_statistical_mode(self, mode_abs_freq:int , output_weights:Dict) -> Tuple[List, Dict]:
        aux = deepcopy(output_weights)
        num_occurences_outputs_on_seq = {output:0 for output in output_weights.keys()}
        seq = []
        for i in range(mode_abs_freq):
            seq.append(self.__func_call_prov.mode_output)
            for output in aux:
                aux[output] -= 1
                if aux[output] == 0:
                    seq.append(pickle.loads(output))
                    num_occurences_outputs_on_seq[output] += 1
                    aux[output] = output_weights[output]
        return seq, num_occurences_outputs_on_seq
    
    def __get_remaining_outputs_on_weighted_seq(self, num_occurences_each_output:Dict) -> Dict:
        remaining_outputs = {}
        for output in self.__func_call_prov.outputs:
            if(output['value'] == self.__func_call_prov.mode_output): continue
            key = pickle.dumps(output['value'])
            if(output['freq'] > num_occurences_each_output[key]):
                remaining_outputs[key] = output['freq'] - num_occurences_each_output[key]
        return remaining_outputs

    def __get_end_of_output_seq_with_interleaved_remaining_outputs(self, remaining_outputs:Dict) -> List:
        seq = []
        while len(remaining_outputs) > 0:
            aux = {}
            for output_value in remaining_outputs:
                seq.append(pickle.loads(output_value))
                remaining_outputs[output_value] -= 1
                if remaining_outputs[output_value] > 0:
                    aux[output_value] = remaining_outputs[output_value]
            remaining_outputs = aux
        return seq