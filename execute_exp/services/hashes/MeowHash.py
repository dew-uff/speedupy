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


# --- Class implementation ---
class MeowHash(Hash):
    """
    Actual implementation of MeowHash v0.5 through a C++ wrapper, using ctypes.
    """

    def __init__(self, serializer, seed_ptr=None):
        super().__init__(serializer)
        self.seed = seed_ptr

    # Overrides the _hash method of the parent class.
    def _hash(self, data: bytes) -> str:
        if not isinstance(data, bytes):
            raise TypeError("MeowHash requires 'bytes' as input.")

        data_len = len(data)

        # Creates a contiguous C memory block and copies the serialized bytes into it.
        c_buffer = (ctypes.c_char * data_len).from_buffer_copy(data)

        # Gets the memory address (pointer) of the C buffer.
        c_ptr = ctypes.addressof(c_buffer)

        # Call into the C++ code:
        lib = _get_library()
        if self.seed is None:
            self.seed = lib.GetMeowDefaultSeed()
        result = lib.MeowHash_32(
            self.seed, ctypes.c_uint64(data_len), ctypes.c_void_p(c_ptr)
        )

        return f"{result:08x}"
