"""A server backend whose driver is not installed fails with a clear message,
and nothing else needs it (D7: the server backends are optional extras)."""

import contextlib
import importlib
import os
import sys
import unittest
from unittest.mock import Mock, patch

from remove_paths import remove_paths

from execute_exp.services import factory
from execute_exp.services.storages.FileSystemStorage import FileSystemStorage
from setup_exp.services.environment_service import init_env

# Database module -> (extra of the pip install, import roots of its driver).
BACKENDS = {
    "entities.MySQLDatabase": ("mysql", ("mysql",)),
    "entities.MongoDatabase": ("mongo", ("pymongo", "gridfs")),
    "entities.GridFSDatabase": ("mongo", ("pymongo", "gridfs")),
    "entities.RedisDatabase": ("redis", ("redis",)),
    "entities.MemcachedDatabase": ("memcached", ("pymemcache",)),
}
ALL_DRIVER_ROOTS = ("mysql", "pymongo", "gridfs", "redis", "pymemcache")


_ABSENT = object()


@contextlib.contextmanager
def drivers_hidden(roots, forget=()):
    """Make ``import <root>`` raise ImportError, for each of ``roots``.

    A submodule that is already imported would be found without its parent
    being looked at, so every loaded name under a root is hidden too. The
    modules in ``forget`` are dropped, to be imported again inside the block.

    Only the entries touched here are put back on exit. ``patch.dict`` would
    restore all of ``sys.modules`` and so forget whatever was first imported
    inside the block, numpy for one, which then loads a second time.
    """
    hide = {}
    for root in roots:
        for name in list(sys.modules):
            if name == root or name.startswith(root + "."):
                hide[name] = None
        hide[root] = None
    for name in forget:
        hide.setdefault(name, _ABSENT)

    saved = {name: sys.modules.get(name, _ABSENT) for name in hide}
    try:
        for name, value in hide.items():
            if value is _ABSENT:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
        yield
    finally:
        for name, value in saved.items():
            if value is _ABSENT:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


class TestMissingDrivers(unittest.TestCase):
    def import_without(self, module_name, roots):
        # Import it again: the copy in sys.modules found its driver.
        with drivers_hidden(roots, forget=[module_name]):
            return importlib.import_module(module_name)

    def test_each_backend_names_the_extra_that_installs_its_driver(self):
        for module_name, (extra, roots) in BACKENDS.items():
            with self.subTest(module=module_name):
                with self.assertRaises(ImportError) as raised:
                    self.import_without(module_name, roots)

                message = str(raised.exception)
                self.assertIn(f"The {extra} backend needs the ", message)
                self.assertIn(f'pip install "speedupy[{extra}]"', message)
                # The driver's own error is kept as the cause.
                self.assertIsInstance(raised.exception.__cause__, ImportError)

    def test_a_missing_driver_does_not_leave_a_broken_module_behind(self):
        before = {name: sys.modules.get(name) for name in BACKENDS}

        for module_name, (_extra, roots) in BACKENDS.items():
            with self.assertRaises(ImportError):
                self.import_without(module_name, roots)

        self.assertEqual({name: sys.modules.get(name) for name in BACKENDS}, before)


class TestNoDriverNeededForTheDefaultInstall(unittest.TestCase):
    """The ``file`` and ``sqlite`` storages work with no server driver."""

    def setUp(self):
        remove_paths(".speedupy")
        self.addCleanup(remove_paths, ".speedupy")
        # Hide the drivers, and drop the Database modules that already imported
        # them, so that importing one of them again would fail.
        hiding = drivers_hidden(ALL_DRIVER_ROOTS, forget=list(BACKENDS))
        hiding.__enter__()
        self.addCleanup(hiding.__exit__, None, None, None)

    def test_setup_with_the_file_and_sqlite_storages(self):
        for storage in ("file", "sqlite"):
            with self.subTest(storage=storage):
                remove_paths(".speedupy")
                init_env(storage)
                self.assertTrue(os.path.isfile(".speedupy/speedupy.db"))
                self.assertTrue(os.path.isdir(".speedupy/cache"))

        for module_name in BACKENDS:
            self.assertNotIn(module_name, sys.modules)

    def test_execution_builds_the_file_storage(self):
        settings = Mock(storage=["file"], serializer=["pickle"])
        with patch.object(factory, "SpeeduPySettings", return_value=settings):
            storage = factory._init_storage()

        self.assertIsInstance(storage, FileSystemStorage)

    def test_execution_builds_the_sqlite_storage(self):
        init_env("sqlite")
        settings = Mock(storage=["sqlite"], serializer=["pickle"])
        with patch.object(factory, "SpeeduPySettings", return_value=settings):
            storage = factory._init_storage()

        self.assertEqual(type(storage).__name__, "SQLiteStorage")


if __name__ == "__main__":
    unittest.main()
