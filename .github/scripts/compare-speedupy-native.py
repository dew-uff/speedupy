"""Compare the binaries of native/lib/ with the speedupy-native 0.1.0 wheels.

One-off check of issue #112, run by .github/workflows/compare-native.yml on
each of the five platforms; both files leave the repository once the result
is written in the pull request.

Each hash is computed twice for the same input and seed: through SpeeduPy's
hash class (the binary of native/lib/ for this platform) and through the
installed speedupy_native module. The inputs are the reference inputs of
native_reference_values.py with their seeds, then random inputs (fixed RNG
seed, so every platform sees the same ones) with random 64-bit seeds.
"""

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "test"))

RNG_SEED = 112
RANDOM_INPUTS = 20000


def random_cases(rng):
    """(data, seed) pairs: every length up to 300, then longer ones."""
    for i in range(RANDOM_INPUTS):
        if i < 3000:
            length = i % 301
        elif i < 19900:
            length = rng.randrange(301, 65537)
        else:
            length = rng.randrange(65537, 2**21)
        yield rng.randbytes(length), rng.getrandbits(64)


def main():
    # Imported here, after sys.path holds the checkout and test/.
    import speedupy_native
    from test_execute_exp.test_services.test_hashes import (
        native_reference_values as ref,
    )

    from execute_exp.services.hashes import native
    from execute_exp.services.hashes.A5Hash import A5Hash
    from execute_exp.services.hashes.MeowHash import MeowHash
    from execute_exp.services.hashes.MuseairBFastHash import MuseairBFastHash

    platform = native.platform_name()
    has_meow = native.is_available("meow")
    if has_meow != speedupy_native.HAS_MEOWHASH:
        sys.exit(
            f"{platform}: native/lib/ has MeowHash={has_meow}, "
            f"speedupy-native has HAS_MEOWHASH={speedupy_native.HAS_MEOWHASH}"
        )

    reference = [(ref.INPUTS[name], seed) for name, seed in sorted(ref.A5HASH)]
    cases = reference + list(random_cases(random.Random(RNG_SEED)))

    counts = {}
    mismatches = []

    def compare(hash_name, ours, theirs, data, seed):
        counts[hash_name] = counts.get(hash_name, 0) + 1
        if ours != theirs:
            mismatches.append((hash_name, len(data), seed, ours, theirs))

    for data, seed in cases:
        compare(
            "a5hash",
            int(A5Hash(None, seed)._hash(data), 16),
            speedupy_native.a5hash_128_64(data, seed),
            data,
            seed,
        )
        compare(
            "museair",
            int(MuseairBFastHash(None, seed)._hash(data), 16),
            speedupy_native.museair_bfast_64(data, seed),
            data,
            seed,
        )
        if has_meow:
            compare(
                "meowhash",
                int(MeowHash(None)._hash(data), 16),
                speedupy_native.meowhash_32(data),
                data,
                None,
            )

    for hash_name, length, seed, ours, theirs in mismatches[:20]:
        print(
            f"MISMATCH {hash_name} len={length} seed={seed}: "
            f"native/lib {ours:#x}, speedupy-native {theirs:#x}"
        )
    summary = ", ".join(f"{name} {n}" for name, n in counts.items())
    verdict = "all equal" if not mismatches else f"{len(mismatches)} differ"
    line = f"| {platform} | {summary} | {verdict} |"
    print(line)
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
