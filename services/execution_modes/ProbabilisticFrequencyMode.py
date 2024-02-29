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
    
    #TODO Necessário adicionar muitos testes unitários!!!
    def _calculate_weighted_output_seq(self):
        mode_abs_freq = None
        for output in self.__func_call_prov.outputs:
            if output['value'] == self.__func_call_prov.mode_output:
                mode_abs_freq = output['freq']
                break
        
        output_weights = {}
        for output in self.__func_call_prov.outputs:
            if output['value'] == self.__func_call_prov.mode_output: continue
            key = pickle.dumps(output['value'])
            output_weights[key] = ceil(mode_abs_freq/output['freq'])

        aux = deepcopy(output_weights)
        num_occurences_outputs_on_seq = {output:0 for output in output_weights.keys()}
        self.__func_call_prov.weighted_output_seq = []
        for i in range(mode_abs_freq):
            self.__func_call_prov.weighted_output_seq.append(self.__func_call_prov.mode_output)
            for output_value in aux:
                aux[output_value] -= 1
                if aux[output_value] == 0:
                    self.__func_call_prov.weighted_output_seq.append(pickle.loads(output_value))
                    num_occurences_outputs_on_seq[output_value] += 1
                    aux[output_value] = output_weights[output_value]

        remaining_outputs = {}
        for output in self.__func_call_prov.outputs:
            if(output['value'] == self.__func_call_prov.mode_output): continue
            key = pickle.dumps(output['value'])
            if(output['freq'] > num_occurences_outputs_on_seq[key]):
                remaining_outputs[key] = output['freq'] - num_occurences_outputs_on_seq[key]

        while len(remaining_outputs) > 0:
            aux = {}
            for output_value in remaining_outputs:
                self.__func_call_prov.weighted_output_seq.append(pickle.loads(output_value))
                remaining_outputs[output_value] -= 1
                if remaining_outputs[output_value] > 0:
                    aux[output_value] = remaining_outputs[output_value]
            remaining_outputs = aux
