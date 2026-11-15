import ctypes

from execute_exp.services.hashes.Hash import Hash
from execute_exp.services.hashes.native import load_native_library

LIBRARY = "libmeow.so"


def _get_library():
    lib = load_native_library(LIBRARY)
    # Define the C function signatures (idempotent).
    lib.MeowHash_32.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_void_p]
    lib.MeowHash_32.restype = ctypes.c_uint32
    lib.GetMeowDefaultSeed.restype = ctypes.c_void_p
    return lib


# --- Implementação da classe ---
class MeowHash(Hash):
    """
    Implementação real do MeowHash v0.5 via wrapper C++, usando ctypes.
    """

    def __init__(self, serializer, seed_ptr=None):
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
        lib = _get_library()
        if self.seed is None:
            self.seed = lib.GetMeowDefaultSeed()
        result = lib.MeowHash_32(
            self.seed, ctypes.c_uint64(data_len), ctypes.c_void_p(c_ptr)
        )

        return f"{result:08x}"
