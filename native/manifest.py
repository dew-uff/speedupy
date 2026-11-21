"""Write native/manifest.json: where each binary of native/lib/ came from.

Usage: python native/manifest.py <run-url> <toolchain-dir>

<run-url> is the workflow run that built the binaries. <toolchain-dir> holds
one <platform>.txt per platform, the toolchain lines the build printed. The
manifest records, for each platform folder, its wheel platform tag and the
toolchain, and for each binary its hash, its size, its sha256 and the source
it was built from (submodule commit and wrapper). The workflow
.github/workflows/native.yml runs this in its last job, from a checkout with
the submodules, after downloading every platform's binaries into native/lib/.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# Folder of native/lib/ -> the platform tag of the wheel that would carry it
# (the PyPI task of RETROFIT.md builds one wheel per folder).
PLATFORM_TAGS = {
    "linux-x86_64": "manylinux_2_28_x86_64",
    "linux-aarch64": "manylinux_2_28_aarch64",
    "windows-amd64": "win_amd64",
    "macos-x86_64": "macosx_10_12_x86_64",
    "macos-arm64": "macosx_11_0_arm64",
}

# Library base name -> (hash name in SpeeduPy, submodule, wrapper)
SOURCES = {
    "a5hash": ("a5hash", "native/vendor/a5hash", "native/src/a5hash_wrapper.c"),
    "meow": ("meowhash", "native/vendor/meow_hash", "native/src/meow_wrapper.cpp"),
    "museair": ("museair", "native/vendor/museair", "native/museair/src/lib.rs"),
}


def _git(*args):
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _submodule_commit(path):
    # "160000 commit <sha>\t<path>": the commit the superproject pins.
    return _git("ls-tree", "HEAD", path).split()[2]


def _submodule_url(path):
    return _git("config", "-f", ".gitmodules", f"submodule.{path}.url")


def _base_name(filename):
    stem = filename.split(".")[0]
    return stem[3:] if stem.startswith("lib") else stem


def main(run_url, toolchain_dir):
    sources = {}
    for hash_name, submodule, wrapper in SOURCES.values():
        sources[hash_name] = {
            "repository": _submodule_url(submodule),
            "commit": _submodule_commit(submodule),
            "submodule": submodule,
            "wrapper": wrapper,
            "wrapper_blob": _git("rev-parse", f"HEAD:{wrapper}"),
        }

    platforms = {}
    for folder in sorted((HERE / "lib").iterdir()):
        if folder.name not in PLATFORM_TAGS:
            sys.exit(f"native/lib/{folder.name}: not a known platform folder")
        toolchain = Path(toolchain_dir) / f"{folder.name}.txt"
        binaries = {}
        for binary in sorted(folder.iterdir()):
            data = binary.read_bytes()
            binaries[binary.name] = {
                "hash": SOURCES[_base_name(binary.name)][0],
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        platforms[folder.name] = {
            "platform_tag": PLATFORM_TAGS[folder.name],
            "toolchain": toolchain.read_text().splitlines(),
            "binaries": binaries,
        }

    missing = set(PLATFORM_TAGS) - set(platforms)
    if missing:
        sys.exit(f"native/lib/ lacks {', '.join(sorted(missing))}")

    manifest = {
        "built_by": run_url,
        "built_from": _git("rev-parse", "HEAD"),
        "sources": sources,
        "platforms": platforms,
    }
    path = HERE / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(path.read_text())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
