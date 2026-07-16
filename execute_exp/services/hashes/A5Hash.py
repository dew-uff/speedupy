import ctypes
import os
from execute_exp.services.hashes.Hash import Hash


# --- Load shared library (.so) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(current_dir, "liba5hash.so")

try:
    a5hash_lib = ctypes.CDLL(lib_path)
except OSError as e:
    raise ImportError(f"Erro ao carregar liba5hash.so: {e}")


# --- Define C function signature ---
a5hash_lib.a5hash_128_64.argtypes = [
    ctypes.c_void_p,   # data pointer
    ctypes.c_size_t,   # length
    ctypes.c_uint64,   # seed
]

a5hash_lib.a5hash_128_64.restype = ctypes.c_uint64


# --- Hash implementation ---
class A5Hash(Hash):
    """
    Implementação do a5hash-128.64 via wrapper C usando ctypes.
    
    - Usa a versão 128-bit do algoritmo
    - Retorna apenas os 64 bits inferiores (padrão SMHasher)
    """

    def __init__(self, serializer, seed: int = 0):
        super().__init__(serializer)
        self.seed = seed

    def _hash(self, data: bytes) -> str:
        if not isinstance(data, bytes):
            raise TypeError("A5Hash requer 'bytes' como entrada.")

        data_len = len(data)

        # Create contiguous C buffer (same pattern as MuseAir)
        c_buffer = (ctypes.c_char * data_len).from_buffer_copy(data)
        c_ptr = ctypes.addressof(c_buffer)

        # Call shared library
        result = a5hash_lib.a5hash_128_64(
            ctypes.c_void_p(c_ptr),
            ctypes.c_size_t(data_len),
            ctypes.c_uint64(self.seed)
        )

        # Return as hex string (64-bit → 16 hex chars)
        return f"{result:016x}"