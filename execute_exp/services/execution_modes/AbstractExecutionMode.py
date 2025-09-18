from abc import ABC, abstractmethod
from execute_exp.entitites.Metadata import Metadata
from execute_exp.entitites.FunctionCallProv import FunctionCallProv
from execute_exp.services.serializers.Serializer import Serializer


class AbstractExecutionMode(ABC):
    def __init__(self, serializer: Serializer, min_num_exec: int):
        self._serializer = serializer
        self._min_num_exec = min_num_exec

    @abstractmethod
    def func_call_can_be_cached(self, fc_prov: FunctionCallProv) -> bool: pass

    @abstractmethod
    def get_func_call_cache(self, fc_prov: FunctionCallProv): pass

    def func_call_acted_as_expected(self, fc_prov: FunctionCallProv, metadata: Metadata): pass  # Implemented by each subclass except ProbabilisticFrequencyMode!

    @property
    def min_num_exec(self):
        return self._min_num_exec