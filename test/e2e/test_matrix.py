"""End-to-end oracle over the options a user can type (Retrofit T17).

The full product of the options is far too large to run, so the server-free
job runs a pairwise covering array: every pair of values of two different
options appears in at least one row. The table is a literal, generated once and
committed, so the set of combinations is reviewable and does not move between
runs. ``test_the_table_covers_every_valid_pair`` checks the claim without
running any process. To change an option, regenerate the table (greedy, rows
taken in lexicographic order of the product, the default row first) and review
the diff.

Columns: hash, memory architecture, retrieval strategy, retrieval execution
mode, serializer, storage, corpus script.
"""

import itertools

import pytest
from harness import assert_oracle, corpus_scripts, run_oracle

HASHES = ("md5", "murmur", "xxhash", "meowhash", "museair", "a5hash")
MEM_ARCHS = ("0-dict", "1-dict", "2-dict", "2-dict-fast")
STRATEGIES = ("lazy", "function", "eager")
EXEC_MODES = ("sequential", "thread")
SERIALIZERS = ("pickle", "cloudpickle")
STORAGES = ("sqlite", "file")
SCRIPTS = ("kwargs_nested.py", "pandas_args.py", "recursive.py", "std_streams.py")
VALUES = (HASHES, MEM_ARCHS, STRATEGIES, EXEC_MODES, SERIALIZERS, STORAGES, SCRIPTS)

NATIVE_HASH_LIBRARIES = {
    "meowhash": "libmeow.so",
    "museair": "libmuseair.so",
    "a5hash": "liba5hash.so",
}

# Combinations that fail today, each with its issue. The pairs are left out of
# the covering array below and held by their own strict xfail rows.
KNOWN_DEFECTS = (
    (
        (
            "xxhash",
            "0-dict",
            "eager",
            "sequential",
            "cloudpickle",
            "file",
            "recursive.py",
        ),
        "#87: 0-dict never hits the cache with eager retrieval",
    ),
    (
        (
            "xxhash",
            "2-dict-fast",
            "eager",
            "thread",
            "cloudpickle",
            "sqlite",
            "recursive.py",
        ),
        "#88: SQLite loader thread has no connection",
    ),
)


def _is_known_defect_pair(row):
    _, mem, strategy, mode, _, storage, _ = row
    return (mem == "0-dict" and strategy == "eager") or (
        storage == "sqlite" and mode == "thread"
    )


# Row 1 is the default of every option. Rows 2-31 complete the pairs (rows
# 26-31 add pandas_args.py, #110; the 25 before them are unchanged).
PAIRWISE = (
    (
        "xxhash",
        "2-dict-fast",
        "eager",
        "sequential",
        "cloudpickle",
        "sqlite",
        "recursive.py",
    ),
    ("md5", "0-dict", "lazy", "sequential", "pickle", "file", "kwargs_nested.py"),
    ("murmur", "1-dict", "function", "thread", "cloudpickle", "file", "std_streams.py"),
    (
        "meowhash",
        "2-dict",
        "function",
        "sequential",
        "pickle",
        "sqlite",
        "std_streams.py",
    ),
    ("museair", "2-dict", "eager", "thread", "pickle", "file", "recursive.py"),
    (
        "meowhash",
        "2-dict-fast",
        "lazy",
        "thread",
        "cloudpickle",
        "file",
        "kwargs_nested.py",
    ),
    ("a5hash", "1-dict", "lazy", "sequential", "pickle", "sqlite", "kwargs_nested.py"),
    ("a5hash", "0-dict", "function", "thread", "cloudpickle", "file", "recursive.py"),
    (
        "museair",
        "0-dict",
        "lazy",
        "sequential",
        "cloudpickle",
        "sqlite",
        "std_streams.py",
    ),
    ("murmur", "2-dict", "lazy", "sequential", "pickle", "sqlite", "kwargs_nested.py"),
    (
        "xxhash",
        "2-dict-fast",
        "function",
        "thread",
        "pickle",
        "file",
        "kwargs_nested.py",
    ),
    ("md5", "1-dict", "eager", "sequential", "cloudpickle", "sqlite", "recursive.py"),
    ("md5", "2-dict", "function", "thread", "cloudpickle", "file", "std_streams.py"),
    (
        "a5hash",
        "2-dict-fast",
        "eager",
        "sequential",
        "pickle",
        "sqlite",
        "std_streams.py",
    ),
    ("murmur", "0-dict", "lazy", "sequential", "pickle", "sqlite", "recursive.py"),
    (
        "murmur",
        "2-dict-fast",
        "eager",
        "sequential",
        "pickle",
        "sqlite",
        "kwargs_nested.py",
    ),
    ("xxhash", "0-dict", "lazy", "sequential", "pickle", "sqlite", "std_streams.py"),
    ("meowhash", "1-dict", "eager", "sequential", "pickle", "sqlite", "recursive.py"),
    (
        "museair",
        "1-dict",
        "function",
        "sequential",
        "pickle",
        "sqlite",
        "kwargs_nested.py",
    ),
    (
        "md5",
        "2-dict-fast",
        "lazy",
        "sequential",
        "pickle",
        "sqlite",
        "kwargs_nested.py",
    ),
    ("xxhash", "1-dict", "lazy", "sequential", "pickle", "sqlite", "kwargs_nested.py"),
    ("xxhash", "2-dict", "lazy", "sequential", "pickle", "sqlite", "kwargs_nested.py"),
    (
        "meowhash",
        "0-dict",
        "lazy",
        "sequential",
        "pickle",
        "sqlite",
        "kwargs_nested.py",
    ),
    (
        "museair",
        "2-dict-fast",
        "lazy",
        "sequential",
        "pickle",
        "sqlite",
        "kwargs_nested.py",
    ),
    ("a5hash", "2-dict", "lazy", "sequential", "pickle", "sqlite", "kwargs_nested.py"),
    ("md5", "0-dict", "lazy", "sequential", "pickle", "sqlite", "pandas_args.py"),
    (
        "murmur",
        "1-dict",
        "function",
        "thread",
        "cloudpickle",
        "file",
        "pandas_args.py",
    ),
    ("xxhash", "2-dict", "eager", "sequential", "pickle", "sqlite", "pandas_args.py"),
    (
        "meowhash",
        "2-dict-fast",
        "lazy",
        "sequential",
        "pickle",
        "sqlite",
        "pandas_args.py",
    ),
    ("museair", "0-dict", "lazy", "sequential", "pickle", "sqlite", "pandas_args.py"),
    ("a5hash", "0-dict", "lazy", "sequential", "pickle", "sqlite", "pandas_args.py"),
)


def _id(row):
    return "-".join(row[:6]) + "-" + row[6].removesuffix(".py")


def _options(row):
    hash_, mem, strategy, mode, serializer, _, _ = row
    return (
        "--hash", hash_,
        "--mem-arch", mem,
        "--retrieval-strategy", strategy,
        "--retrieval-exec-mode", mode,
        "--serializer", serializer,
    )  # fmt: skip


def params(rows):
    out = []
    for row in rows:
        marks = []
        library = NATIVE_HASH_LIBRARIES.get(row[0])
        if library:
            marks.append(pytest.mark.native(library))
        out.append(pytest.param(row, marks=marks, id=_id(row)))
    return out


def run_row(row, tmp_path):
    script, storage = row[6], row[5]
    assert_oracle(run_oracle(script, storage, tmp_path, _options(row)))


def _pairs(row):
    return {
        ((i, row[i]), (j, row[j]))
        for i in range(len(row))
        for j in range(i + 1, len(row))
    }


def test_the_table_covers_every_valid_pair():
    wanted = set()
    for row in itertools.product(*VALUES):
        if not _is_known_defect_pair(row):
            wanted |= _pairs(row)
    covered = set()
    for row in PAIRWISE:
        assert not _is_known_defect_pair(row), row
        covered |= _pairs(row)
    assert wanted - covered == set()
    assert len(set(PAIRWISE)) == len(PAIRWISE)


def test_the_first_row_is_the_default_of_every_option():
    assert PAIRWISE[0] == (
        "xxhash",
        "2-dict-fast",
        "eager",
        "sequential",
        "cloudpickle",
        "sqlite",
        "recursive.py",
    )


def test_the_tables_name_corpus_scripts():
    scripts = {row[6] for row in PAIRWISE}
    assert scripts <= set(corpus_scripts())
    assert set(SCRIPTS) == set(corpus_scripts())


@pytest.mark.parametrize("row", params(PAIRWISE))
def test_the_option_matrix_changes_nothing_but_the_work_done(row, tmp_path):
    run_row(row, tmp_path)


@pytest.mark.parametrize(
    "row",
    [
        pytest.param(
            row,
            marks=pytest.mark.xfail(strict=True, reason=reason),
            id=_id(row),
        )
        for row, reason in KNOWN_DEFECTS
    ],
)
def test_the_known_defects_stay_visible(row, tmp_path):
    run_row(row, tmp_path)
