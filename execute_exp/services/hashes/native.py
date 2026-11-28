"""Loading of the native hash libraries (a5hash, MuseAir).

The binaries are versioned in native/lib/, one folder per platform, and built
by the workflow .github/workflows/native.yml (native/README.md). A library is
loaded the first time its hash is used, so a platform without it loses only
that hash: md5 and xxhash work everywhere.
"""

import ctypes
import functools
import platform
import struct
import sys
from pathlib import Path

LIBRARY_ROOT = Path(__file__).resolve().parents[3] / "native" / "lib"

# (sys.platform, platform.machine() in lower case) -> folder of native/lib/.
PLATFORM_FOLDERS = {
    ("linux", "x86_64"): "linux-x86_64",
    ("linux", "aarch64"): "linux-aarch64",
    ("linux", "arm64"): "linux-aarch64",
    ("win32", "amd64"): "windows-amd64",
    ("win32", "x86_64"): "windows-amd64",
    ("darwin", "x86_64"): "macos-x86_64",
    ("darwin", "arm64"): "macos-arm64",
}

# Folder -> the libraries built for it.
PLATFORM_LIBRARIES = {
    "linux-x86_64": ("a5hash", "museair"),
    "linux-aarch64": ("a5hash", "museair"),
    "windows-amd64": ("a5hash", "museair"),
    "macos-x86_64": ("a5hash", "museair"),
    "macos-arm64": ("a5hash", "museair"),
}


def platform_folder():
    """The folder of native/lib/ for the running interpreter, or None.

    A 32-bit interpreter has none, even on a 64-bit system.
    """
    if struct.calcsize("P") != 8:
        return None
    return PLATFORM_FOLDERS.get((sys.platform, platform.machine().lower()))


def platform_name():
    """The running platform, as error messages name it."""
    folder = platform_folder()
    if folder:
        return folder
    bits = struct.calcsize("P") * 8
    return f"{sys.platform}-{platform.machine().lower() or 'unknown'} ({bits}-bit)"


def library_filename(library, system=None):
    """File name of ``library`` ("a5hash" or "museair") on ``system``."""
    system = system or sys.platform
    if system == "win32":
        return f"{library}.dll"
    if system == "darwin":
        return f"lib{library}.dylib"
    return f"lib{library}.so"


def is_available(library):
    """Whether native/lib/ has ``library`` for the running platform."""
    return library in PLATFORM_LIBRARIES.get(platform_folder(), ())


@functools.lru_cache(maxsize=None)
def load_native_library(library: str, hash_name: str) -> ctypes.CDLL:
    """Load ``library`` of the running platform the first time it is needed.

    Raises ``ImportError`` naming ``hash_name`` and the platform when the
    platform has no such library or it cannot be loaded, so that only the hash
    that needs it fails.
    """
    folder = platform_folder()
    if not is_available(library):
        raise ImportError(
            f"The hash {hash_name} is not available on {platform_name()}: "
            "SpeeduPy has no native binaries for this platform. The hashes md5 "
            "and xxhash work on every platform."
        )
    path = LIBRARY_ROOT / folder / library_filename(library)
    try:
        return ctypes.CDLL(str(path))
    except OSError as e:
        raise ImportError(
            f"Could not load the native library of the hash {hash_name} "
            f"on {folder} ({path}): {e}"
        ) from e
