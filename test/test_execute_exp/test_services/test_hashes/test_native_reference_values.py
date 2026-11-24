"""The native hashes reproduce the values of the original libraries.

Each value goes through the hash class, as SpeeduPy calls it, and the binary
of the running platform (native/lib/). A platform without a library skips its
tests (see ``native`` in test/conftest.py); anywhere else a wrong value fails.
"""

import pytest

from execute_exp.services.hashes.A5Hash import A5Hash
from execute_exp.services.hashes.MeowHash import MeowHash
from execute_exp.services.hashes.MuseairBFastHash import MuseairBFastHash
from test_execute_exp.test_services.test_hashes.native_reference_values import (
    A5HASH,
    INPUTS,
    MEOWHASH,
    MUSEAIR,
)


@pytest.mark.native("a5hash")
@pytest.mark.parametrize(("name", "seed"), sorted(A5HASH))
def test_a5hash(name, seed):
    expected = f"{A5HASH[(name, seed)]:016x}"
    assert A5Hash(serializer=None, seed=seed)._hash(INPUTS[name]) == expected


@pytest.mark.native("museair")
@pytest.mark.parametrize(("name", "seed"), sorted(MUSEAIR))
def test_museair(name, seed):
    expected = f"{MUSEAIR[(name, seed)]:016x}"
    assert MuseairBFastHash(serializer=None, seed=seed)._hash(INPUTS[name]) == expected


@pytest.mark.native("meow")
@pytest.mark.parametrize("name", sorted(MEOWHASH))
def test_meowhash(name):
    expected = f"{MEOWHASH[name]:08x}"
    assert MeowHash(serializer=None)._hash(INPUTS[name]) == expected
