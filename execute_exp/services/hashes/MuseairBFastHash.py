import ctypes
import os
from execute_exp.services.hashes.Hash import Hash


# --- Load shared library (.so) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(current_dir, "libmuseair.so")

try:
    museair_lib = ctypes.CDLL(lib_path)
except OSError as e:
    raise ImportError(f"Erro ao carregar libmuseair.so: {e}")


# --- Define C function signature ---
museair_lib.museair_bfast_64.argtypes = [
    ctypes.c_void_p,                 # data pointer
    ctypes.c_size_t,                 # length
    ctypes.c_uint64,                 # seed
    ctypes.POINTER(ctypes.c_uint64)  # output pointer
]

museair_lib.museair_bfast_64.restype = None


# --- Hash implementation ---
class MuseairBFastHash(Hash):
    """
    Implementação do MuseAir BFast (64-bit) via Rust (.so) usando ctypes.
    """

    def __init__(self, serializer, seed: int = 0):
        super().__init__(serializer)
        self.seed = seed

    def _hash(self, data: bytes) -> str:
        if not isinstance(data, bytes):
            raise TypeError("MuseAir requer 'bytes' como entrada.")

        data_len = len(data)

        # Create contiguous C buffer
        c_buffer = (ctypes.c_char * data_len).from_buffer_copy(data)
        c_ptr = ctypes.addressof(c_buffer)

        # Prepare output variable
        out = ctypes.c_uint64()

        # Call shared library function
        museair_lib.museair_bfast_64(
            ctypes.c_void_p(c_ptr),
            ctypes.c_size_t(data_len),
            ctypes.c_uint64(self.seed),
            ctypes.byref(out)
        )

        # Return as hex string (16 chars for 64-bit)
        return f"{out.value:016x}"