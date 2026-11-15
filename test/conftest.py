"""pytest harness for SpeeduPy: safe by default.

This file lives in ``test/`` and ``test/`` never gains an ``__init__.py``.
A conftest at the repository root would be imported as ``speedupy.conftest``
(the root is a package), and ``from speedupy import ...`` would then break.

What it does, and why:

1. ``sys.argv`` is trimmed when this file is imported, before any test module
   loads. ``speedupy.py`` parses ``sys.argv`` at import, so any pytest option
   (``-q``, ``-k``, ``-m``) would otherwise make argparse exit with status 2.
2. The session runs in a fresh scratch directory. The paths in
   ``constantes.py`` are relative, so ``.speedupy/`` and the scripts the tests
   write land there and never in the checkout.
3. The markers come from ``MARKER_MAP`` below, so the test files stay
   untouched.
4. A test with a server marker is deselected unless ``SPEEDUPY_TEST_SERVERS=1``.
   With it set, every server is probed once at the start and the session aborts
   naming the unreachable ones: a missing server is an error, never a skip.
   The probe is skipped under ``--collect-only``, which touches no server.
5. The modules that cannot be imported without a native library are kept out
   of collection, and the tests marked ``native`` are deselected. Task 12 of the
   retrofit removes ``NOT_COLLECTED`` and replaces the deselection by a skip.
6. ``sys.version_info`` is restored after every test, because
   ``test/test_util.py`` leaves it changed and pytest reads it. Task 8 widens
   this to the other process state a test may leave behind.
"""
import os
import shutil
import socket
import sys
import tempfile
from pathlib import Path

import pytest

# Must stay first: nothing below may import a module that builds SpeeduPySettings.
sys.argv = sys.argv[:1]

TEST_DIR = Path(__file__).resolve().parent
ENV_SERVERS = "SPEEDUPY_TEST_SERVERS"

# The hosts and ports are the ones the code under test uses.
SERVERS = {
    "mysql": ("127.0.0.1", 3306),
    "mongo": ("localhost", 27017),
    "redis": ("localhost", 6379),
    "memcached": ("localhost", 11211),
}
ALL_SERVERS = tuple(SERVERS)

# Modules that cannot be imported without a native library: they load libmeow.so,
# liba5hash.so or libmuseair.so at import time. Task 12 loads each one on first
# use and removes this list.
NOT_COLLECTED = [
    "test_execute_exp/test_services/test_factory.py",
    "test_execute_exp/test_services/test_hashes/test_A5Hash.py",
    "test_execute_exp/test_services/test_hashes/test_MeowHash.py",
    "test_execute_exp/test_services/test_hashes/test_MuseairBFastHash.py",
]
collect_ignore = list(NOT_COLLECTED)

# Path relative to ``test/`` (a directory, a file, or ``file::Class::test``) ->
# markers. A whole file is marked when any of its fixtures touches a
# server, even for a test that does not: ``setUp`` and ``tearDown`` run for each
# one of them.
MARKER_MAP = {
    # setUp connects to MySQL; tearDown flushes Redis, MongoDB and Memcached and
    # drops the MySQL database, for every test of the class, including the folder
    # and SQLite ones. Task 15 splits that lifecycle.
    "test_setup_exp/test_services/test_environment_service.py": ALL_SERVERS,
    # BancoMySQL() connects to MySQL in setUp, even though the cursor is mocked
    # right after.
    "test_entities/test_MySQL.py": ("mysql",),
    "test_execute_exp/test_services/test_storages/test_MySQLStorage.py": ("mysql",),
    "test_execute_exp/test_services/test_storages/test_RedisStorage.py": ("redis",),
    "test_execute_exp/test_services/test_storages/test_MongoStorage.py": ("mongo",),
    "test_execute_exp/test_services/test_storages/test_GridFSStorage.py": ("mongo",),
    "test_execute_exp/test_services/test_storages/test_MongoWithFileSystemStorage.py": ("mongo",),
    "test_execute_exp/test_services/test_storages/test_MongoWithGridFSStorage.py": ("mongo",),
    "test_execute_exp/test_services/test_memory_architectures/test_MemcachedWriteBackMemArch.py": ("memcached",),
    "test_execute_exp/test_services/test_memory_architectures/test_MemcachedWriteThroughMemArch.py": ("memcached",),
    # Not collected today (see NOT_COLLECTED); the markers are ready for Task 12.
    "test_execute_exp/test_services/test_factory.py": ("native",),
    "test_execute_exp/test_services/test_hashes/test_A5Hash.py": ("native",),
    "test_execute_exp/test_services/test_hashes/test_MeowHash.py": ("native",),
    "test_execute_exp/test_services/test_hashes/test_MuseairBFastHash.py": ("native",),
    # These build SpeeduPy(), which calls get_hash(): the default hash is a native
    # one. The key may go down to a test: file::Class::test.
    "test_speedupy_execution_modes.py::TestSpeeduPyExecMode::test_initialize_speedupy_on_no_cache_exec_mode_with_time_measure": ("native",),
    "test_speedupy_execution_modes.py::TestSpeeduPyExecMode::test_initialize_speedupy_on_no_cache_exec_mode_without_time_measure": ("native",),
    "test_speedupy_execution_modes.py::TestSpeeduPyExecMode::test_initialize_speedupy_using_cache_exec_modes_with_and_without_time_measure_and_profile": ("native",),
}

_original_cwd = os.getcwd()
_scratch_dir = None
_deselected = {"server": 0, "native": 0}


def _servers_enabled() -> bool:
    return os.environ.get(ENV_SERVERS) == "1"


def _is_reachable(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def _markers_of(item):
    file_part = Path(str(item.path)).resolve().relative_to(TEST_DIR).as_posix()
    rest = item.nodeid.partition("::")[2]
    test_id = f"{file_part}::{rest}" if rest else file_part
    for key, markers in MARKER_MAP.items():
        if test_id == key or test_id.startswith((key + "::", key.rstrip("/") + "/")):
            yield from markers


class _RootIsNotAPackage:
    """Collect the repository root as a plain directory, never as a package.

    The root has an ``__init__.py``, so pytest would make it a ``Package``. Its
    setup imports that file and prepends the *parent* of the checkout to
    ``sys.path``. From then on ``importlib.reload(speedupy)`` finds the package
    ``speedupy/__init__.py`` (empty) before ``speedupy.py``, and the reload no
    longer redefines anything. This is a plugin object, not a hook of this file,
    because a conftest only applies to the directories below it.
    """

    @pytest.hookimpl(tryfirst=True)
    def pytest_collect_directory(self, path, parent):
        if path == parent.config.rootpath:
            return pytest.Dir.from_parent(parent, path=path)
        return None


def pytest_configure(config):
    global _scratch_dir
    config.pluginmanager.register(_RootIsNotAPackage(), "speedupy-root-is-not-a-package")
    _scratch_dir = tempfile.mkdtemp(prefix="speedupy-tests-")
    os.chdir(_scratch_dir)


def pytest_unconfigure(config):
    os.chdir(_original_cwd)
    if _scratch_dir:
        shutil.rmtree(_scratch_dir, ignore_errors=True)


def pytest_sessionstart(session):
    if not _servers_enabled() or session.config.option.collectonly:
        return
    unreachable = [f"{name} ({host}:{port})" for name, (host, port) in SERVERS.items()
                   if not _is_reachable(host, port)]
    if unreachable:
        pytest.exit(f"{ENV_SERVERS}=1, but these servers are unreachable: "
                    f"{', '.join(unreachable)}. Start them, or unset {ENV_SERVERS} "
                    "to run only the tests that need no server.", returncode=1)


@pytest.fixture(autouse=True)
def _restore_sys_version_info():
    saved = sys.version_info
    yield
    sys.version_info = saved


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    for item in items:
        for marker in _markers_of(item):
            item.add_marker(getattr(pytest.mark, marker))

    kept, deselected = [], []
    for item in items:
        if item.get_closest_marker("native"):
            _deselected["native"] += 1  # Task 12 replaces this by a skip.
            deselected.append(item)
        elif not _servers_enabled() and any(item.get_closest_marker(name) for name in ALL_SERVERS):
            _deselected["server"] += 1
            deselected.append(item)
        else:
            kept.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = kept


def pytest_terminal_summary(terminalreporter):
    if _deselected["server"]:
        terminalreporter.write_line(
            f"{_deselected['server']} tests that need a server were deselected: "
            f"set {ENV_SERVERS}=1 to run them (see AGENTS.md).")
    if _deselected["native"]:
        terminalreporter.write_line(
            f"{_deselected['native']} tests that need a native library were deselected "
            "(Task 12 of the retrofit loads the libraries on demand).")
