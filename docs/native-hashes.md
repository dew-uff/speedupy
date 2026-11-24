# Native hashes: the binaries in the repository

Decision D3 of `RETROFIT.md`, as revised by issue #112. This document is the
design of the three native hashes: where their sources are, how their binaries
are built, versioned and loaded, how they are validated, and how they will be
packaged. The procedure to rebuild the binaries is `native/README.md`.

## Why the binaries live here

SpeeduPy offers six hashes: `md5` (standard library), `murmur` (`mmh3`) and
`xxhash` (`xxhash`), which install from wheels on every platform, and three
native ones, `a5hash`, `meowhash` and `museair`. Until #112 the native ones
were `.so` files compiled by hand on one Linux machine, not versioned, from
sources in three other repositories.

D3, as the maintainers decided it on 2026-11-19, moved them to a separate
package, `speedupy-native` (issue #106). Issue #112 replaced that with the
binaries inside this repository:

- **One repository, one release.** Whoever joins the project clones
  `speedupy` and has everything: no second repository, no second PyPI project,
  no version pin between the two.
- **The native hashes are options, not requirements.** SpeeduPy runs with
  `md5`, `murmur` and `xxhash` on any platform. A platform with no native
  binary loses only those hashes, as the lazy loading of Task 12 already
  allowed.
- **Reproducibility comes from the version of `speedupy`.** A release carries
  the binaries of its time; a binary built later goes out only in a later
  release.

## The sources

The three algorithms are git submodules of the original repositories, at the
commits the measurements used. These commits are never moved silently: a new
commit changes the hash values, and MuseAir's later versions are a different
algorithm.

| Hash | Submodule | Original | Commit | Language | License |
| :--- | :--- | :--- | :--- | :--- | :--- |
| a5hash | `native/vendor/a5hash` | `avaneev/a5hash` | `10492dbe8c34ae043ccbab3fe4b16a2a26eebbc6` (2025-12-19, version 5.25) | C, single header `a5hash.h` | MIT |
| MeowHash 0.5 | `native/vendor/meow_hash` | `cmuratori/meow_hash` | `b080caa7e51576fe3151c8976110df7966fa6a38` (2021-07-02) | C++, `meow_hash_x64_aesni.h` | zlib |
| MuseAir BFast | `native/vendor/museair` | `eternal-io/museair` | `29e56adbc737412d7b6cecfaec73e68e5566a107` (2025-12-21, crate 0.4.0) | Rust crate | MIT or Apache-2.0 |

The original `.so` files were built from personal forks of these repositories
(`JoaoLopez/a5hash` at `7ff7fa3`, `JoaoLopez/meow_hash` at `beeb71f`,
`JoaoLopez/museair` at `91e7304`). Each fork is its original at the commit
above plus a wrapper; none changes an algorithm. The wrappers moved here:

| Wrapper | Exports | Changes from the fork |
| :--- | :--- | :--- |
| `native/src/a5hash_wrapper.c` | `a5hash_128_64(data, len, seed) -> uint64` | an export macro, so that Windows exports the symbol |
| `native/src/meow_wrapper.cpp` | `MeowHash_32(seed, len, data) -> uint32`, `GetMeowDefaultSeed()` | the export macro, English comments, and `MeowHash_C` (never called) left out |
| `native/museair/src/lib.rs` | `museair_bfast_64(data, len, seed, out)` | the function the fork added to the crate, now in a small crate of ours that depends on the original crate by path |

`native/NOTICE` carries the three licenses, since a clone without the
submodules has the binaries but not the sources.

## Layout

```
native/
├── README.md               # the procedure to rebuild the binaries
├── NOTICE                  # the licenses of the three sources
├── manifest.json           # where each binary came from (written by the workflow)
├── lib/<platform>/         # the binaries, versioned
├── src/                    # the C and C++ wrappers
├── museair/                # the MuseAir wrapper crate (Cargo.lock, pinned Rust)
├── vendor/                 # the three submodules
├── build.sh                # build of one Linux or macOS platform
├── build.ps1               # build of Windows x64
├── check.py                # the binaries of one platform against the reference values
└── manifest.py             # writes manifest.json
```

## Platforms

| Folder | Wheel platform tag | a5hash | MuseAir | MeowHash | Built on |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `linux-x86_64` | `manylinux_2_28_x86_64` | `liba5hash.so` | `libmuseair.so` | `libmeow.so` | `ubuntu-24.04`, in the `manylinux_2_28_x86_64` image |
| `linux-aarch64` | `manylinux_2_28_aarch64` | `liba5hash.so` | `libmuseair.so` | no | `ubuntu-24.04-arm`, in the `manylinux_2_28_aarch64` image |
| `windows-amd64` | `win_amd64` | `a5hash.dll` | `museair.dll` | `meow.dll` | `windows-2025`, MSVC |
| `macos-x86_64` | `macosx_10_12_x86_64` | `liba5hash.dylib` | `libmuseair.dylib` | `libmeow.dylib` | `macos-15-intel` |
| `macos-arm64` | `macosx_11_0_arm64` | `liba5hash.dylib` | `libmuseair.dylib` | no | `macos-15` |

The Linux libraries need glibc 2.28 or newer (Debian 10, Ubuntu 18.10, RHEL 8
and later). MeowHash's official implementation exists for x86_64 with AES-NI
only; the project maintains no ARM port, and SpeeduPy does not adopt a
third-party one. Any other platform (32-bit Python, Windows on ARM, a BSD) has
no native binary and keeps the other three hashes.

## Build

Only the workflow `.github/workflows/native.yml` builds the versioned
binaries, on GitHub's runners for the five platforms; nobody compiles them on
their own machine. On `main` it runs only by hand; on any other branch, a push
that changes the sources or the build runs it too, as a check. Each platform
job builds with `native/build.sh` or `native/build.ps1`, then runs
`native/check.py` against the reference values on its own system. The last
job writes `native/manifest.json` and uploads the binaries and the manifest as
the `native-binaries` artifact, which the person rebuilding them commits
(`native/README.md`).

The compiler flags are the ones the original `.so` files were built with:
a5hash with `-O3 -fno-inline`, MeowHash with `-O3 -maes -msse4.1`, MuseAir with
`cargo build --release`; on Windows, MSVC's equivalents (`/O2 /Ob0`, `/O2`).
Flags change speed, never the hash values, but the measurements were taken
with these. The Rust release is pinned in `native/museair/rust-toolchain.toml`
(1.83.0, the minimum the MuseAir crate declares).

The manifest records, for each binary, its hash, size and sha256; for each
platform, its wheel platform tag and the toolchain the build printed; for each
hash, the original repository, the submodule commit and the wrapper (with its
git blob id); and the workflow run and the commit the binaries were built
from. A test checks that the files in `native/lib/` are exactly the ones the
manifest lists, with the same sha256.

## Loading

`execute_exp/services/hashes/native.py` picks the folder of `native/lib/` for
the running interpreter, from `sys.platform` and `platform.machine()` (a
32-bit interpreter has none), and loads the library through `ctypes` the
first time its hash is used. A platform without the library raises an
`ImportError` that names the hash and the platform and says that `md5`,
`murmur` and `xxhash` work everywhere; only that hash fails. The submodules
are needed only to rebuild the binaries: a plain clone runs every hash and can
change any Python code.

## Validation

- **Reference values.** The values of the original `.so` files, for ten
  inputs (empty to 1 MiB) and four seeds, are
  `test/test_execute_exp/test_services/test_hashes/native_reference_values.py`:
  40 for a5hash, 40 for MuseAir, 10 for MeowHash. They come from the
  `speedupy-native` 0.1.0 package (`tests/test_vectors.py`), produced there
  with the original libraries on Linux x86_64. `native/check.py` checks them
  right after each build, and `test_native_reference_values.py` checks them
  through the hash classes, in the `test` job (Linux x86_64) and in the
  `native-platforms` job (Windows x64, macOS x86_64 and arm64, Linux aarch64).
- **Comparison with `speedupy-native` 0.1.0.** Once, during #112, a workflow
  compared on each of the five platforms the binaries of `native/lib/` with
  the published 0.1.0 wheels: the reference inputs and 20000 random inputs
  (every length up to 300 bytes, then up to 2 MiB) with random 64-bit seeds,
  for each hash. Every value was equal on every platform. The result is in the
  pull request of #112.

## Packaging (designed here, built later)

`speedupy` is not installable yet (`package = false`, and about 180 absolute
imports of top-level names such as `util` and `constants`); publishing it on
PyPI is the last task of the retrofit plan. When it is published:

- one wheel per folder of `native/lib/`, carrying that folder's binaries and
  tagged with the platform tag of the table above (and of the manifest);
- one generic wheel (`py3-none-any`) with no binary, for any other platform;
- pip picks the most specific wheel that fits the machine, so a user of a
  platform outside the five gets the generic wheel and the three portable
  hashes.

## Limits

- MeowHash is unavailable on arm64 (see "Platforms"); the other five hashes
  work there. A paper that reports MeowHash numbers says they were measured on
  x86_64.
- MeowHash also needs AES-NI on x86_64, which most x86_64 processors since
  about 2010 have but not all (some Atom and Pentium parts, some virtual
  machines); SpeeduPy does not check the CPU yet, as the original `.so` did
  not, and a runtime check is a follow-up issue.
- MeowHash 0.5 was reclassified by its author after a published cryptanalysis:
  it is not for message authentication nor for hash tables exposed to
  collision attacks. A memoization cache in a non-adversarial setting is
  within its intended use.
- The pinned commits are frozen for the measurements. Upgrading MuseAir to the
  current crate (0.6, a different algorithm) is a new hash name, not a bump.
- The reference values come from the original `.so` files on Linux x86_64,
  through the `speedupy-native` package; the original files are not versioned
  anywhere.
