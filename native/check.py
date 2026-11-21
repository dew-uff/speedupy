"""Check the native libraries of one platform against the reference values.

Usage: python native/check.py <platform>

Loads every library of native/lib/<platform>/ through ctypes, with the
signatures the hash classes use, and compares each result with
test/test_execute_exp/test_services/test_hashes/native_reference_values.py.
Also checks that the folder holds exactly the libraries of that platform.
On a mismatch it prints every value computed here in the format of
native_reference_values.py, for the deliberate move of a submodule
(native/README.md, "Moving a submodule").
The workflow .github/workflows/native.yml runs it on each platform right after
the build; it needs only the standard library, so it runs before SpeeduPy's
dependencies are installed.
"""

import ctypes
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REFERENCE = (
    HERE.parent
    / "test"
    / "test_execute_exp"
    / "test_services"
    / "test_hashes"
    / "native_reference_values.py"
)

# platform -> (prefix, extension, has MeowHash)
PLATFORMS = {
    "linux-x86_64": ("lib", "so", True),
    "linux-aarch64": ("lib", "so", False),
    "windows-amd64": ("", "dll", True),
    "macos-x86_64": ("lib", "dylib", True),
    "macos-arm64": ("lib", "dylib", False),
}


def _load_reference():
    spec = importlib.util.spec_from_file_location("native_reference_values", REFERENCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _buffer(data):
    buffer = (ctypes.c_char * len(data)).from_buffer_copy(data)
    return buffer, ctypes.addressof(buffer)


def check_a5hash(lib, ref):
    lib.a5hash_128_64.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint64]
    lib.a5hash_128_64.restype = ctypes.c_uint64
    for (name, seed), expected in ref.A5HASH.items():
        data = ref.INPUTS[name]
        _, ptr = _buffer(data)
        yield ("a5hash", name, seed, lib.a5hash_128_64(ptr, len(data), seed), expected)


def check_museair(lib, ref):
    lib.museair_bfast_64.argtypes = [
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_uint64,
        ctypes.POINTER(ctypes.c_uint64),
    ]
    lib.museair_bfast_64.restype = None
    for (name, seed), expected in ref.MUSEAIR.items():
        data = ref.INPUTS[name]
        _, ptr = _buffer(data)
        out = ctypes.c_uint64()
        lib.museair_bfast_64(ptr, len(data), seed, ctypes.byref(out))
        yield ("museair", name, seed, out.value, expected)


def check_meowhash(lib, ref):
    lib.MeowHash_32.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_void_p]
    lib.MeowHash_32.restype = ctypes.c_uint32
    lib.GetMeowDefaultSeed.restype = ctypes.c_void_p
    seed = lib.GetMeowDefaultSeed()
    for name, expected in ref.MEOWHASH.items():
        data = ref.INPUTS[name]
        _, ptr = _buffer(data)
        yield ("meowhash", name, None, lib.MeowHash_32(seed, len(data), ptr), expected)


def main(platform):
    if platform not in PLATFORMS:
        sys.exit(f"unknown platform {platform!r}; one of {', '.join(PLATFORMS)}")
    prefix, ext, has_meow = PLATFORMS[platform]
    folder = HERE / "lib" / platform
    checks = {"a5hash": check_a5hash, "museair": check_museair}
    if has_meow:
        checks["meow"] = check_meowhash

    expected_files = {f"{prefix}{base}.{ext}" for base in checks}
    found_files = {p.name for p in folder.iterdir()} if folder.is_dir() else set()
    if found_files != expected_files:
        sys.exit(
            f"{folder}: expected {sorted(expected_files)}, found {sorted(found_files)}"
        )

    ref = _load_reference()
    total = failures = 0
    computed = {}
    for base, check in checks.items():
        lib = ctypes.CDLL(str(folder / f"{prefix}{base}.{ext}"))
        for hash_name, name, seed, got, expected in check(lib, ref):
            total += 1
            key = name if seed is None else (name, seed)
            computed.setdefault(hash_name, {})[key] = got
            if got != expected:
                failures += 1
                print(
                    f"MISMATCH {hash_name} input={name} seed={seed}: "
                    f"got {got:#x}, expected {expected:#x}"
                )
    print(f"{platform}: {total - failures} of {total} reference values match")
    if failures:
        _print_tables(platform, computed)
    return 1 if failures else 0


def _print_tables(platform, computed):
    print(f"\nValues computed on {platform}, as in native_reference_values.py:")
    widths = {"a5hash": 16, "museair": 16, "meowhash": 8}
    for hash_name, values in computed.items():
        print(f"\n{hash_name.upper()} = {{")
        for key, value in values.items():
            # The layout ruff gives the file: double quotes, upper-case digits.
            name = f'("{key[0]}", {key[1]})' if isinstance(key, tuple) else f'"{key}"'
            print(f"    {name}: 0x{value:0{widths[hash_name]}X},")
        print("}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
