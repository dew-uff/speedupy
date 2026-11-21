/*
 * MeowHash 0.5 for SpeeduPy's ctypes loader (execute_exp/services/hashes/MeowHash.py).
 *
 * Taken from https://github.com/JoaoLopez/meow_hash, commit beeb71f, the
 * wrapper the original libmeow.so was built from. The bodies of the two
 * functions SpeeduPy calls are unchanged. Changes: the comments are in
 * English, the export macro was added so that Windows exports the symbols,
 * and MeowHash_C (128-bit result, never called by SpeeduPy) was left out.
 * The algorithm is vendor/meow_hash/meow_hash_x64_aesni.h (submodule, see
 * native/README.md): x86_64 with AES-NI only.
 */
#include <cstdint>
#include "meow_hash_x64_aesni.h"

#if defined(_WIN32)
#define SPEEDUPY_EXPORT __declspec(dllexport)
#else
#define SPEEDUPY_EXPORT __attribute__((visibility("default")))
#endif

// Unmangled names, so that ctypes finds the functions.
extern "C" {

    // Lower 32 bits of the 128-bit MeowHash of data, with Seed.
    SPEEDUPY_EXPORT uint32_t MeowHash_32(void *Seed, uint64_t len, void *data) {
        __m128i hash = MeowHash(Seed, len, data);

        alignas(16) uint64_t out[2];
        _mm_storeu_si128((__m128i*)out, hash);

        return (uint32_t)(out[0]);  // lower 32 bits
    }

    // Pointer to the default seed of MeowHash.
    SPEEDUPY_EXPORT void* GetMeowDefaultSeed() {
        return (void*)MeowDefaultSeed;
    }
}
