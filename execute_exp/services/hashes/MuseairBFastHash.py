import ctypes

from execute_exp.services.hashes.Hash import Hash
from execute_exp.services.hashes.native import load_native_library

LIBRARY = "libmuseair.so"


def _get_library():
    lib = load_native_library(LIBRARY)
    # Define the C function signature (idempotent).
    lib.museair_bfast_64.argtypes = [
        ctypes.c_void_p,  # data pointer
        ctypes.c_size_t,  # length
        ctypes.c_uint64,  # seed
        ctypes.POINTER(ctypes.c_uint64),  # output pointer
    ]
    lib.museair_bfast_64.restype = None
    return lib


# --- Hash implementation ---
class MuseairBFastHash(Hash):
    """
    Implementation of MuseAir BFast (64-bit) through Rust (.so), using ctypes.
    """

    def __init__(self, serializer, seed: int = 0):
        super().__init__(serializer)
        self.seed = seed

    def _hash(self, data: bytes) -> str:
        if not isinstance(data, bytes):
            raise TypeError("MuseAir requires 'bytes' as input.")

        data_len = len(data)

        # Create contiguous C buffer
        c_buffer = (ctypes.c_char * data_len).from_buffer_copy(data)
        c_ptr = ctypes.addressof(c_buffer)

        # Prepare output variable
        out = ctypes.c_uint64()

        # Call shared library function
        _get_library().museair_bfast_64(
            ctypes.c_void_p(c_ptr),
            ctypes.c_size_t(data_len),
            ctypes.c_uint64(self.seed),
            ctypes.byref(out),
        )

        # Return as hex string (16 chars for 64-bit)
        return f"{out.value:016x}"
