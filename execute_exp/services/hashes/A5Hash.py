import ctypes

from execute_exp.services.hashes.Hash import Hash
from execute_exp.services.hashes.native import load_native_library

LIBRARY = "liba5hash.so"


def _get_library():
    lib = load_native_library(LIBRARY)
    # Define the C function signature (idempotent).
    lib.a5hash_128_64.argtypes = [
        ctypes.c_void_p,  # data pointer
        ctypes.c_size_t,  # length
        ctypes.c_uint64,  # seed
    ]
    lib.a5hash_128_64.restype = ctypes.c_uint64
    return lib


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
        result = _get_library().a5hash_128_64(
            ctypes.c_void_p(c_ptr),
            ctypes.c_size_t(data_len),
            ctypes.c_uint64(self.seed),
        )

        # Return as hex string (64-bit → 16 hex chars)
        return f"{result:016x}"
