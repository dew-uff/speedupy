import ctypes
import os
from execute_exp.services.hashes.Hash import Hash 

# Espelha a struct MeowU128 definida no wrapper C++.
class MeowU128(ctypes.Structure):
    _fields_ = [
        ("low", ctypes.c_uint64),
        ("high", ctypes.c_uint64)
    ]

# --- Carregamento da biblioteca ---
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(current_dir, 'libmeow.so')

try:
    meow_lib = ctypes.CDLL(lib_path)
except OSError as e:
    raise ImportError(f"Erro ao carregar libmeow.so: {e}")

# --- Definição das funções C ---
meow_lib.MeowHash_C.argtypes = [
    ctypes.c_void_p,   # Seed 
    ctypes.c_uint64,   # Tamanho dos dados
    ctypes.c_void_p    # Ponteiro para os bytes
]
meow_lib.MeowHash_C.restype = MeowU128

meow_lib.GetMeowDefaultSeed.restype = ctypes.c_void_p
MeowDefaultSeed = meow_lib.GetMeowDefaultSeed()

# --- Implementação da classe ---
class MeowHash(Hash):
    """
    Implementação real do MeowHash v0.5 via wrapper C++, usando ctypes.
    """
    
    def __init__(self, serializer, seed_ptr=MeowDefaultSeed):
        super().__init__(serializer)
        self.seed = seed_ptr

    # Sobrescreve o método _hash da classe pai.
    def _hash(self, data: bytes) -> str:
        if not isinstance(data, bytes):
            raise TypeError("MeowHash requer 'bytes' como entrada.")

        data_len = len(data)
        
        # Cria um bloco de memória C contíguo e copia os bytes serializados.
        c_buffer = (ctypes.c_char * data_len).from_buffer_copy(data)
        
        # Obtém o endereço de memória (ponteiro) do buffer C.
        c_ptr = ctypes.addressof(c_buffer)

        # Chamada ao Código C++:
        result = meow_lib.MeowHash_C(
            self.seed,
            ctypes.c_uint64(data_len),
            ctypes.c_void_p(c_ptr) 
        )

        # Converte a struct para string hexadecimal.
        return f"{result.high:016x}{result.low:016x}"