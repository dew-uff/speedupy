"""End-to-end oracle over the server storages and the Memcached architectures.

One row per server storage and per Memcached architecture (Retrofit T17). It is
marked mysql, mongo, redis and memcached in ``MARKER_MAP``, so it runs only in
the server job (``SPEEDUPY_TEST_SERVERS=1``) and erases data there. Memcached
holds the cache in RAM, so its rows keep a local storage.

Columns: see ``test_matrix.py``.
"""

import pytest
from test_matrix import params, run_row

SERVER_MATRIX = (
    (
        "xxhash",
        "2-dict-fast",
        "eager",
        "sequential",
        "cloudpickle",
        "redis",
        "recursive.py",
    ),
    ("md5", "1-dict", "lazy", "sequential", "pickle", "mongo", "kwargs_nested.py"),
    (
        "md5",
        "2-dict",
        "function",
        "sequential",
        "cloudpickle",
        "gridfs",
        "std_streams.py",
    ),
    (
        "xxhash",
        "2-dict-fast",
        "lazy",
        "sequential",
        "pickle",
        "mongo-file",
        "recursive.py",
    ),
    (
        "xxhash",
        "2-dict",
        "eager",
        "sequential",
        "cloudpickle",
        "mongo-gridfs",
        "kwargs_nested.py",
    ),
    ("md5", "1-dict", "eager", "sequential", "pickle", "mysql", "std_streams.py"),
    (
        "xxhash",
        "memcached-wt",
        "eager",
        "sequential",
        "cloudpickle",
        "file",
        "recursive.py",
    ),
    (
        "xxhash",
        "memcached-wb",
        "lazy",
        "sequential",
        "pickle",
        "sqlite",
        "kwargs_nested.py",
    ),
)


@pytest.mark.parametrize("row", params(SERVER_MATRIX))
def test_the_server_option_matrix_changes_nothing_but_the_work_done(row, tmp_path):
    run_row(row, tmp_path)
