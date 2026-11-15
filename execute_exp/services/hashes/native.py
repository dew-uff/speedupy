import ctypes
import functools
import os

LIBRARY_DIR = os.path.dirname(os.path.abspath(__file__))


@functools.lru_cache(maxsize=None)
def load_native_library(filename: str) -> ctypes.CDLL:
    """Load ``filename`` from this directory the first time it is needed.

    Raises ``ImportError`` naming the library when it cannot be loaded, so that
    only the hash that needs it fails.
    """
    path = os.path.join(LIBRARY_DIR, filename)
    try:
        return ctypes.CDLL(path)
    except OSError as e:
        raise ImportError(f"Could not load the native library {filename}: {e}") from e
