"""pytest harness for SpeeduPy: safe by default.

This file lives in ``test/`` and ``test/`` never gains an ``__init__.py``.
A conftest at the repository root would be imported as ``speedupy.conftest``
(the root is a package), and ``from speedupy import ...`` would then break.

What it does, and why:

1. ``sys.argv`` is trimmed when this file is imported, before any test module
   loads. ``speedupy.py`` parses ``sys.argv`` at import, so any pytest option
   (``-q``, ``-k``, ``-m``) would otherwise make argparse exit with status 2.
2. The session runs in a fresh scratch directory. The paths in
   ``constants.py`` are relative, so ``.speedupy/`` and the scripts the tests
   write land there and never in the checkout.
3. The markers come from ``MARKER_MAP`` below, so the test files stay
   untouched.
4. A test with a server marker is deselected unless ``SPEEDUPY_TEST_SERVERS=1``.
   With it set, every server is probed once at the start and the session aborts
   naming the unreachable ones: a missing server is an error, never a skip.
   The probe is skipped under ``--collect-only``, which touches no server.
5. A test marked ``native`` needs the native libraries it names (``NATIVE_MAP``
   below, or ``@pytest.mark.native("meow")`` on the test): "a5hash", "meow" or
   "museair", the libraries of ``native/lib/``. It is skipped, with the library
   and the platform in the reason, only where ``native/lib/`` has no such
   library for the running platform (MeowHash on arm64, any of them outside
   the five platforms). Where it has one, the test runs: a missing or broken
   file is a failure.
6. The process state a test may leave behind is restored after every test, so
   that no test depends on another and the order can be random (Task 8): the
   instances of the ``SingletonMeta`` classes and their attributes,
   ``sys.argv``, ``sys.version_info`` and the current directory. A test that
   needs a changed value still changes it; the fixture only undoes it.
   ``sys.version_info`` matters most: pytest reads it.
"""

import os
import shutil
import socket
import sys
import tempfile
from pathlib import Path

import pytest

from SingletonMeta import SingletonMeta

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

# Path relative to ``test/`` (a directory, a file, or ``file::Class::test``) ->
# markers. A whole file is marked when any of its fixtures touches a
# server, even for a test that does not: ``setUp`` and ``tearDown`` run for each
# one of them.
MARKER_MAP = {
    # One row per server storage and per Memcached architecture; it runs only in
    # the server job, so every server is needed for the whole test.
    "e2e/test_matrix_servers.py": ALL_SERVERS,
    # setUp connects to MySQL; tearDown flushes Redis, MongoDB and Memcached and
    # drops the MySQL database, for every test of the class. The folder and
    # SQLite tests live in test_environment_service_local.py, which touches no
    # server and has no entry here.
    "test_setup_exp/test_services/test_environment_service.py": ALL_SERVERS,
    # MySQLDatabase() connects to MySQL in setUp, even though the cursor is mocked
    # right after.
    "test_entities/test_MySQLDatabase.py": ("mysql",),
    "test_execute_exp/test_services/test_storages/test_MySQLStorage.py": ("mysql",),
    "test_execute_exp/test_services/test_storages/test_RedisStorage.py": ("redis",),
    "test_execute_exp/test_services/test_storages/test_MongoStorage.py": ("mongo",),
    "test_execute_exp/test_services/test_storages/test_GridFSStorage.py": ("mongo",),
    "test_execute_exp/test_services/test_storages/test_MongoWithFileSystemStorage.py": (
        "mongo",
    ),
    "test_execute_exp/test_services/test_storages/test_MongoWithGridFSStorage.py": (
        "mongo",
    ),
    "test_execute_exp/test_services/test_memory_architectures/test_MemcachedWriteBackMemArch.py": (
        "memcached",
    ),
    "test_execute_exp/test_services/test_memory_architectures/test_MemcachedWriteThroughMemArch.py": (
        "memcached",
    ),
}

# Path relative to ``test/`` -> the native libraries (of ``native/lib/``) the
# tests below it need. Same keys as ``MARKER_MAP``.
NATIVE_MAP = {
    "test_execute_exp/test_services/test_hashes/test_A5Hash.py": ("a5hash",),
    "test_execute_exp/test_services/test_hashes/test_MeowHash.py": ("meow",),
    "test_execute_exp/test_services/test_hashes/test_MuseairBFastHash.py": ("museair",),
}

_original_cwd = os.getcwd()
_scratch_dir = None
_deselected = {"server": 0}


def _servers_enabled() -> bool:
    return os.environ.get(ENV_SERVERS) == "1"


def _is_reachable(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def _test_id(item):
    file_part = Path(str(item.path)).resolve().relative_to(TEST_DIR).as_posix()
    rest = item.nodeid.partition("::")[2]
    return f"{file_part}::{rest}" if rest else file_part


def _matching(mapping, test_id):
    for key, value in mapping.items():
        if test_id == key or test_id.startswith((key + "::", key.rstrip("/") + "/")):
            yield value


def _markers_of(item):
    for markers in _matching(MARKER_MAP, _test_id(item)):
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
    config.pluginmanager.register(
        _RootIsNotAPackage(), "speedupy-root-is-not-a-package"
    )
    _scratch_dir = tempfile.mkdtemp(prefix="speedupy-tests-")
    os.chdir(_scratch_dir)


def pytest_unconfigure(config):
    os.chdir(_original_cwd)
    if _scratch_dir:
        shutil.rmtree(_scratch_dir, ignore_errors=True)


def pytest_sessionstart(session):
    if not _servers_enabled() or session.config.option.collectonly:
        return
    unreachable = [
        f"{name} ({host}:{port})"
        for name, (host, port) in SERVERS.items()
        if not _is_reachable(host, port)
    ]
    if unreachable:
        pytest.exit(
            f"{ENV_SERVERS}=1, but these servers are unreachable: "
            f"{', '.join(unreachable)}. Start them, or unset {ENV_SERVERS} "
            "to run only the tests that need no server.",
            returncode=1,
        )


@pytest.fixture(autouse=True)
def _restore_process_state():
    """Undo what a test changed in the process, whether it passed or not.

    ``SingletonMeta`` keeps one instance per class for the life of the process.
    A test that builds one under a mock, or assigns to an attribute of one,
    would otherwise hand that to every test after it. The instances that
    exist before the test are kept, with their attributes put back (the
    attributes are restored by name, so an object mutated in place is not
    undone); the ones the test created are dropped.
    """
    instances = dict(SingletonMeta._instances)
    attributes = {cls: dict(vars(obj)) for cls, obj in instances.items()}
    argv, argv_items = sys.argv, list(sys.argv)
    version_info = sys.version_info
    cwd = os.getcwd()
    yield
    sys.version_info = version_info
    argv[:] = argv_items
    sys.argv = argv
    os.chdir(cwd)
    SingletonMeta._instances.clear()
    SingletonMeta._instances.update(instances)
    for cls, saved in attributes.items():
        obj = instances[cls]
        vars(obj).clear()
        vars(obj).update(saved)


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    for item in items:
        for marker in _markers_of(item):
            item.add_marker(getattr(pytest.mark, marker))
        for libraries in _matching(NATIVE_MAP, _test_id(item)):
            item.add_marker(pytest.mark.native(*libraries))

    kept, deselected = [], []
    for item in items:
        if not _servers_enabled() and any(
            item.get_closest_marker(name) for name in ALL_SERVERS
        ):
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
            f"set {ENV_SERVERS}=1 to run them (see AGENTS.md)."
        )


def pytest_runtest_setup(item):
    # Imported here: the module must not load before sys.argv is trimmed, and
    # it imports nothing that builds SpeeduPySettings.
    from execute_exp.services.hashes import native

    names = [name for marker in item.iter_markers("native") for name in marker.args]
    known = {lib for libs in native.PLATFORM_LIBRARIES.values() for lib in libs}
    unknown = sorted(set(names) - known)
    if unknown:
        # A misspelt name would skip the test everywhere, silently.
        pytest.fail(
            f"unknown native library {', '.join(unknown)}: use one of "
            f"{', '.join(sorted(known))}",
            pytrace=False,
        )
    missing = [name for name in names if not native.is_available(name)]
    if missing:
        pytest.skip(
            f"native/lib/ has no {', '.join(missing)} for {native.platform_name()}"
        )
