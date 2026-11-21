/*
 * a5hash-128.64 for SpeeduPy's ctypes loader (execute_exp/services/hashes/A5Hash.py).
 *
 * Taken from https://github.com/JoaoLopez/a5hash, commit 7ff7fa3, the wrapper
 * the original liba5hash.so was built from. The function body is unchanged;
 * only the export macro was added, so that Windows exports the symbol too.
 * The algorithm is vendor/a5hash/a5hash.h (submodule, see native/README.md).
 */
#include "a5hash.h"
#include <stdint.h>
#include <stddef.h>

#if defined(_WIN32)
#define SPEEDUPY_EXPORT __declspec(dllexport)
#else
#define SPEEDUPY_EXPORT __attribute__((visibility("default")))
#endif

// SMHasher-compatible: a5hash-128.64
SPEEDUPY_EXPORT uint64_t a5hash_128_64(const void* data, size_t len, uint64_t seed) {
    uint64_t high;
    uint64_t low = a5hash128(data, len, seed, &high);
    return low;  // lower 64 bits
}
