import ctypes
import hashlib
import importlib
import json
import sys
from unittest.mock import patch

import pytest

from execute_exp.services.factory import get_hash
from execute_exp.services.hashes import native
from execute_exp.services.hashes.MD5Hash import MD5Hash
from execute_exp.services.hashes.XXHashHash import XXHashHash

NATIVE_HASHES = [
    ("execute_exp.services.hashes.A5Hash", "A5Hash", "a5hash"),
    (
        "execute_exp.services.hashes.MuseairBFastHash",
        "MuseairBFastHash",
        "museair",
    ),
]

MANIFEST = native.LIBRARY_ROOT.parent / "manifest.json"


@pytest.fixture(autouse=True)
def clear_library_cache():
    # A library loaded by an earlier test must not hide the case under test.
    native.load_native_library.cache_clear()
    yield
    native.load_native_library.cache_clear()


@pytest.fixture
def no_native_libraries():
    """Make every attempt to load a library fail, as with a broken binary."""
    with patch.object(ctypes, "CDLL", side_effect=OSError("file not found")):
        yield


@pytest.fixture
def settings():
    with patch("execute_exp.services.factory.SpeeduPySettings") as settings:
        settings().serializer = ["pickle"]
        yield settings()


def _on(system, machine, pointer_size=8):
    """Pretend to run on ``system`` (sys.platform) and ``machine``."""
    real_calcsize = native.struct.calcsize
    return (
        patch.object(sys, "platform", system),
        patch.object(native.platform, "machine", return_value=machine),
        patch.object(
            native.struct,
            "calcsize",
            side_effect=lambda f: pointer_size if f == "P" else real_calcsize(f),
        ),
    )


def test_get_hash_returns_md5_without_native_libraries(no_native_libraries, settings):
    settings.hash = ["md5"]
    assert isinstance(get_hash(), MD5Hash)


def test_get_hash_returns_xxhash_without_native_libraries(
    no_native_libraries, settings
):
    settings.hash = ["xxhash"]
    assert isinstance(get_hash(), XXHashHash)


@pytest.mark.parametrize(("module", "class_name", "hash_name"), NATIVE_HASHES)
def test_native_module_imports_without_its_library(
    no_native_libraries, module, class_name, hash_name
):
    assert hasattr(importlib.import_module(module), class_name)


@pytest.mark.parametrize(("module", "class_name", "hash_name"), NATIVE_HASHES)
def test_native_hash_fails_on_first_use_naming_the_hash_and_the_platform(
    no_native_libraries, module, class_name, hash_name
):
    hash_class = getattr(importlib.import_module(module), class_name)
    with pytest.raises(ImportError) as error:
        hash_class(serializer=None)._hash(b"data")
    assert hash_name in str(error.value)
    assert native.platform_name() in str(error.value)


@pytest.mark.parametrize(
    ("system", "machine", "folder"),
    [
        ("linux", "x86_64", "linux-x86_64"),
        ("linux", "aarch64", "linux-aarch64"),
        ("win32", "AMD64", "windows-amd64"),
        ("darwin", "x86_64", "macos-x86_64"),
        ("darwin", "arm64", "macos-arm64"),
    ],
)
def test_each_platform_has_its_folder(system, machine, folder):
    a, b, c = _on(system, machine)
    with a, b, c:
        assert native.platform_folder() == folder
        assert native.platform_name() == folder


@pytest.mark.parametrize(
    ("system", "machine", "pointer_size", "name"),
    [
        ("freebsd14", "amd64", 8, "freebsd14-amd64 (64-bit)"),
        ("win32", "ARM64", 8, "win32-arm64 (64-bit)"),
        ("linux", "x86_64", 4, "linux-x86_64 (32-bit)"),
    ],
)
def test_a_platform_outside_the_five_has_no_folder(system, machine, pointer_size, name):
    a, b, c = _on(system, machine, pointer_size)
    with a, b, c:
        assert native.platform_folder() is None
        assert native.platform_name() == name


@pytest.mark.parametrize(
    ("system", "filename"),
    [
        ("linux", "liba5hash.so"),
        ("win32", "a5hash.dll"),
        ("darwin", "liba5hash.dylib"),
    ],
)
def test_library_filename_follows_the_system(system, filename):
    assert native.library_filename("a5hash", system) == filename


@pytest.mark.parametrize(
    ("system", "machine", "path"),
    [
        ("linux", "x86_64", "linux-x86_64/libmuseair.so"),
        ("linux", "aarch64", "linux-aarch64/libmuseair.so"),
        ("win32", "AMD64", "windows-amd64/museair.dll"),
        ("darwin", "x86_64", "macos-x86_64/libmuseair.dylib"),
        ("darwin", "arm64", "macos-arm64/libmuseair.dylib"),
    ],
)
def test_the_library_is_loaded_from_the_platform_folder(system, machine, path):
    a, b, c = _on(system, machine)
    with a, b, c, patch.object(ctypes, "CDLL") as cdll:
        native.load_native_library("museair", "museair")
    cdll.assert_called_once_with(str(native.LIBRARY_ROOT / path))


def test_a_platform_outside_the_five_names_the_hash_and_the_platform():
    a, b, c = _on("freebsd14", "amd64")
    with a, b, c, patch.object(ctypes, "CDLL") as cdll:
        with pytest.raises(ImportError, match=r"a5hash.*freebsd14-amd64 \(64-bit\)"):
            native.load_native_library("a5hash", "a5hash")
    cdll.assert_not_called()


def test_the_manifest_lists_the_five_platforms_and_their_libraries():
    manifest = json.loads(MANIFEST.read_text())
    assert set(manifest["platforms"]) == set(native.PLATFORM_LIBRARIES)
    system_of = {"linux": "linux", "windows": "win32", "macos": "darwin"}
    for folder, libraries in native.PLATFORM_LIBRARIES.items():
        system = system_of[folder.split("-")[0]]
        expected = {native.library_filename(lib, system) for lib in libraries}
        assert set(manifest["platforms"][folder]["binaries"]) == expected, folder


def test_every_binary_matches_the_sha256_of_the_manifest():
    manifest = json.loads(MANIFEST.read_text())
    on_disk = {
        path.relative_to(native.LIBRARY_ROOT).as_posix()
        for path in native.LIBRARY_ROOT.rglob("*")
        if path.is_file()
    }
    listed = {
        f"{folder}/{name}"
        for folder, entry in manifest["platforms"].items()
        for name in entry["binaries"]
    }
    assert on_disk == listed
    for folder, entry in manifest["platforms"].items():
        for name, binary in entry["binaries"].items():
            data = (native.LIBRARY_ROOT / folder / name).read_bytes()
            assert hashlib.sha256(data).hexdigest() == binary["sha256"], name
