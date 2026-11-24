#!/usr/bin/env bash
# Builds the native hash libraries of one Linux or macOS platform into
# native/lib/<platform>/. Windows is native/build.ps1. The workflow
# .github/workflows/native.yml runs this; native/README.md says how and when.
#
# Usage: native/build.sh <platform>
#   <platform>: linux-x86_64, linux-aarch64, macos-x86_64 or macos-arm64
#
# Needs the submodules (git submodule update --init), a C and a C++ compiler,
# and rustup (the Rust release is pinned in native/museair/rust-toolchain.toml).
# Linux builds run inside a manylinux_2_28 container, so the libraries load
# on any Linux with glibc 2.28 or newer.
#
# The compiler flags are the ones the original .so files were built with
# (the README of each fork): a5hash with -O3 -fno-inline, MeowHash with -O3
# -maes -msse4.1, MuseAir with `cargo build --release`. They change speed,
# never the hash values, but the measurements were taken with them.
set -euo pipefail

platform="${1:?usage: native/build.sh <platform>}"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out="$here/lib/$platform"

case "$platform" in
  linux-x86_64)  shared=(-shared -fPIC -Wl,--as-needed);     ext=so;    meow=yes ;;
  linux-aarch64) shared=(-shared -fPIC -Wl,--as-needed);     ext=so;    meow=no ;;
  macos-x86_64)  shared=(-dynamiclib -Wl,-dead_strip_dylibs); ext=dylib; meow=yes
                 export MACOSX_DEPLOYMENT_TARGET=10.12 ;;
  macos-arm64)   shared=(-dynamiclib -Wl,-dead_strip_dylibs); ext=dylib; meow=no
                 export MACOSX_DEPLOYMENT_TARGET=11.0 ;;
  *) echo "unknown platform: $platform" >&2; exit 2 ;;
esac

for submodule in a5hash meow_hash museair; do
  if [ -z "$(ls -A "$here/vendor/$submodule" 2>/dev/null)" ]; then
    echo "native/vendor/$submodule is empty: run git submodule update --init" >&2
    exit 1
  fi
done

rm -rf "$out"
mkdir -p "$out"

# The toolchain lines go to the log and to native/build/<platform>.txt, which
# native/manifest.py copies into the manifest.
echo "== toolchain"
mkdir -p "$here/build"
{
  cc --version | head -n 1
  c++ --version | head -n 1
  (cd "$here/museair" && rustc --version && cargo --version)
} | tee "$here/build/$platform.txt"

echo "== a5hash"
cc -O3 -fno-inline "${shared[@]}" -I "$here/vendor/a5hash" \
  -o "$out/liba5hash.$ext" "$here/src/a5hash_wrapper.c"

if [ "$meow" = yes ]; then
  echo "== MeowHash"
  c++ -O3 -maes -msse4.1 "${shared[@]}" -I "$here/vendor/meow_hash" \
    -o "$out/libmeow.$ext" "$here/src/meow_wrapper.cpp"
else
  echo "== MeowHash: not built, x86_64 with AES-NI only"
fi

echo "== MuseAir"
(cd "$here/museair" && cargo build --release --locked)
cp "$here/museair/target/release/libmuseair_ffi.$ext" "$out/libmuseair.$ext"

# A macOS library records its own path as its install name; the build path
# would end up in the binary. ctypes loads by full path, so a relative name
# is enough.
if [ "$ext" = dylib ]; then
  for lib in "$out"/*; do
    install_name_tool -id "@rpath/$(basename "$lib")" "$lib"
  done
fi

echo "== built"
ls -l "$out"
for lib in "$out"/*; do
  if [ "$ext" = so ]; then
    readelf -d "$lib" | grep NEEDED || true
  else
    otool -L "$lib"
  fi
done
