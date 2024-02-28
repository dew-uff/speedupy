from services.execution_modes.AbstractExecutionMode import AbstractExecutionMode
from data_access import get_func_call_prov
from constantes import Constantes

class ProbabilisticCountingMode(AbstractExecutionMode):
    def func_call_can_be_cached(self, func_call_hash:str) -> bool:
        self.__func_call_prov = get_func_call_prov(func_call_hash)
        if self.__func_call_prov.mode_rel_freq is None:
            self._set_helpers()
        return self.__func_call_prov.mode_rel_freq >= Constantes().g_argsp_min_mode_occurrence

    #############TODO!!!!!!!!!!!!!!!!!!!
    def _set_helpers(self):
        output_mode = None
        for output in self.__func_call_prov.outputs:
            pass
