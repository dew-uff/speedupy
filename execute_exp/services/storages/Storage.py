from typing import Dict, Optional

from execute_exp.entitites.CacheData import CacheData
from execute_exp.services.serializers.Serializer import Serializer


class Storage:
    def __init__(self, serializer: Serializer):
        self._serializer = serializer

    def get_all_cached_data(
        self, use_isolated_connection=False
    ) -> Dict[str, CacheData]:
        pass

    def get_cached_data_of_a_function(
        self, func_name: str, use_isolated_connection=False
    ) -> Dict[str, CacheData]:
        pass

    # TODO: ADICIONAR fun_name=None nos métodos que chamam Storage
    def get_cached_data_of_a_function_call(
        self, func_call_hash: str, func_name=None, use_isolated_connection=False
    ) -> Optional[CacheData]:
        pass

    def save_cache_data(
        self, data: Dict[str, CacheData], use_isolated_connection=False
    ) -> None:
        pass
