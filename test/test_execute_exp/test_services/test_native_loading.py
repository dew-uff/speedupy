import ctypes
import importlib
from unittest.mock import patch

import pytest

from execute_exp.services.factory import get_hash
from execute_exp.services.hashes.MD5Hash import MD5Hash
from execute_exp.services.hashes.XXHashHash import XXHashHash

NATIVE_HASHES = [
    ("execute_exp.services.hashes.MeowHash", "MeowHash", "libmeow.so"),
    ("execute_exp.services.hashes.A5Hash", "A5Hash", "liba5hash.so"),
    (
        "execute_exp.services.hashes.MuseairBFastHash",
        "MuseairBFastHash",
        "libmuseair.so",
    ),
]


def _clear_library_cache():
    # A library loaded by an earlier test must not hide the missing one.
    try:
        native = importlib.import_module("execute_exp.services.hashes.native")
    except ImportError:
        return
    native.load_native_library.cache_clear()


@pytest.fixture
def no_native_libraries():
    """Make every attempt to load a ``.so`` fail, as on a checkout without them."""
    _clear_library_cache()
    with patch.object(ctypes, "CDLL", side_effect=OSError("file not found")):
        yield
    _clear_library_cache()


@pytest.fixture
def settings():
    with patch("execute_exp.services.factory.SpeeduPySettings") as settings:
        settings().serializer = ["pickle"]
        yield settings()


def test_get_hash_returns_md5_without_native_libraries(no_native_libraries, settings):
    settings.hash = ["md5"]
    assert isinstance(get_hash(), MD5Hash)


def test_get_hash_returns_xxhash_without_native_libraries(
    no_native_libraries, settings
):
    settings.hash = ["xxhash"]
    assert isinstance(get_hash(), XXHashHash)


@pytest.mark.parametrize(("module", "class_name", "library"), NATIVE_HASHES)
def test_native_module_imports_without_its_library(
    no_native_libraries, module, class_name, library
):
    assert hasattr(importlib.import_module(module), class_name)


@pytest.mark.parametrize(("module", "class_name", "library"), NATIVE_HASHES)
def test_native_hash_fails_on_first_use_naming_its_library(
    no_native_libraries, module, class_name, library
):
    hash_class = getattr(importlib.import_module(module), class_name)
    with pytest.raises(ImportError, match=library.replace(".", r"\.")):
        hash_class(serializer=None)._hash(b"data")
