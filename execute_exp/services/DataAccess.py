from constantes import Constantes
from execute_exp.entitites.FunctionCallProv import FunctionCallProv
from execute_exp.entitites.Metadata import Metadata
from execute_exp.function_calls_prov_table import FunctionCallsProvTable
from execute_exp.services.memory_architecures.AbstractMemArch import AbstractMemArch
from SingletonMeta import SingletonMeta
from util import get_content_json_file


class DataAccess(metaclass=SingletonMeta):
    def __init__(self):
        self.__METADATA = {}
        self._FUNCTIONS_2_HASHES = {}
        self._mem_arch: AbstractMemArch
        self.__function_calls_prov_table: FunctionCallsProvTable

    def init_data_access(self):
        from execute_exp.services.factory import get_hash, get_serializer, init_mem_arch

        self._mem_arch = init_mem_arch()
        self._hash = get_hash()
        self.__function_calls_prov_table = FunctionCallsProvTable(get_serializer())
        self._FUNCTIONS_2_HASHES = get_content_json_file(
            Constantes().EXP_FUNCTIONS_FILENAME
        )

        self._mem_arch.get_initial_cache_entries()
        self.__function_calls_prov_table.get_initial_function_calls_prov_entries()

    def get_function_hash(self, func_qualname: str) -> str:
        return self._FUNCTIONS_2_HASHES[func_qualname]

    ############# CACHE
    def get_id(self, func_qualname, func_args, func_kwargs):
        func_hash = self.get_function_hash(func_qualname)
        return self._hash.get_id(func_hash, func_args, func_kwargs)

    def get_cache_entry(self, func_call_hash, func_qualname):
        return self._mem_arch.get_cache_entry(func_call_hash, func_qualname)

    def create_cache_entry(self, func_call_hash, func_return, func_qualname):
        self._mem_arch.create_cache_entry(func_call_hash, func_return, func_qualname)

    ############# METADATA
    def add_to_metadata(self, func_call_hash: str, metadata: Metadata) -> None:
        if func_call_hash not in self.__METADATA:
            self.__METADATA[func_call_hash] = []
        self.__METADATA[func_call_hash].append(metadata)

    # TODO:TEST
    def get_amount_of_collected_metadata(self, func_call_hash: str) -> int:
        try:
            return len(self.__METADATA[func_call_hash])
        except KeyError:
            return 0

    ############# FUNCTION_CALL_PROV
    def get_function_call_prov_entry(self, func_call_hash: str) -> FunctionCallProv:
        return self.__function_calls_prov_table.get_function_call_prov_entry(
            func_call_hash
        )

    def create_or_update_function_call_prov_entry(
        self, fc_prov: FunctionCallProv
    ) -> None:
        self.__function_calls_prov_table.create_or_update_function_call_prov_entry(
            fc_prov
        )

    def add_all_metadata_collected_to_function_calls_prov(self) -> None:
        self.__function_calls_prov_table.add_all_metadata_collected_to_function_calls_prov(
            self.__METADATA
        )
        self.__METADATA = {}

    def add_metadata_collected_to_a_func_call_prov(
        self, fc_prov: FunctionCallProv
    ) -> None:
        self.__function_calls_prov_table.add_metadata_collected_to_a_func_call_prov(
            fc_prov, self.__METADATA[fc_prov.function_call_hash]
        )
        self.__METADATA.pop(fc_prov.function_call_hash)

    def get_new_cache_entries_size(self) -> int:
        return self._mem_arch.get_new_cache_entries_size()

    def close_data_access(self):
        self._mem_arch.save_new_cache_entries()
        self.__function_calls_prov_table.save_function_calls_prov_entries()
