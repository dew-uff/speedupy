from execute_exp.memory_architectures.AbstractMemArch import AbstractMemArch
from data_access_util import get_file_name, deserialize, serialize
from storage import get_storage, save_storage
from constantes import Constantes
from banco import Banco

#TODO: TEST
class V01MemArch(AbstractMemArch):
    def get_initial_cache_entries(self): pass
    
    def get_cache_entry(self, func_call_hash:str):
        Constantes().CONEXAO_BANCO = Banco(Constantes().BD_PATH)
        list_file_name = get_storage(get_file_name(func_call_hash))
        Constantes().CONEXAO_BANCO.fecharConexao()
        return deserialize(func_call_hash) if len(list_file_name) == 1 else None
    
    def create_cache_entry(self, func_call_hash:str, func_return):
        Constantes().CONEXAO_BANCO = Banco(Constantes().BD_PATH)
        serialize(func_return, func_call_hash)
        save_storage(get_file_name(func_call_hash))
        Constantes().CONEXAO_BANCO.salvarAlteracoes()
        Constantes().CONEXAO_BANCO.fecharConexao()
        
    def save_new_cache_entries(self): pass