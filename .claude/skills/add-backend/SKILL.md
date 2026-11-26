---
name: add-backend
description: Adds a storage, a hash or a memory architecture to SpeeduPy end to end, with its class, tests, factory, command line, documents and CI floors. Use when a new value of -s/--storage, -H/--hash or --mem-arch is wanted.
---

# Adding a backend

A backend is a new value of `--storage`, `--hash` or `--mem-arch`. The names of
these options are repeated in the code and in the tests, and several omissions
fail silently. Follow the common steps, then the section of the kind you add.

## Before writing code

- The issue exists and the solution is agreed there (`CONTRIBUTING.md`).
- A new driver or library is evaluated first with `prove-candidate`.
- Changing an existing hash is not adding one: it changes every cache key.
- Record the test count of the suite before the change (`uv run pytest -q`).

## Common steps

1. **Write the tests first** (`CONTRIBUTING.md`, "Tests").
2. **Write the class.** The base classes are not abstract: their methods are
   `pass`, so a method you forget returns `None` without an error.
3. **Command line,** `execute_exp/parser_params.py`: add the name to its list of
   choices and a line to the matching `*_msg()` function of `--help`.
4. **Factory,** `execute_exp/services/factory.py`: add a branch. The chains have
   no `else`, so a missing branch returns `None`. Import the new module inside
   the function, so a missing driver matters only when the backend is selected.
5. **Factory test:** add the name and the class to the list in
   `test/test_execute_exp/test_services/test_factory.py`, with the marker of
   its server or native library.
6. **Option matrix,** `test/e2e/test_matrix.py`: see "Option matrix" below.
7. **README.md:** the option table under "Execution Options", and "Key
   Features" when it names the backends.
8. **Check the help** shows the name:

   ```bash
   uv run python -c "from execute_exp.parser_params import get_params; get_params()" --help
   ```

## Storage

### Class

`execute_exp/services/storages/<Name>Storage.py`, a subclass of `Storage`,
with the four methods and their `use_isolated_connection` argument:

| Method | Contract |
| :--- | :--- |
| `get_all_cached_data` | A dict of call hash to `CacheData`; `{}` when empty. |
| `get_cached_data_of_a_function` | Only that function's records; `{}` when none. |
| `get_cached_data_of_a_function_call` | The `CacheData`, or `None` when missing. |
| `save_cache_data` | Accepts `{}`; saving an existing record again is harmless. |

- Records arrive with `func_name` set (`function` retrieval) or `None` (`lazy`
  and `eager`). Store and read both.
- `use_isolated_connection=True` comes from a retrieval thread: use a
  connection of its own when the driver's cannot be shared.
- Serialize with `self._serializer`.

A storage keeps its records between processes: the end-to-end oracle runs a
script three times and fails on one that only keeps them in memory.

### A storage that needs no server

Add its name next to `file` and `sqlite` in:

- `STORAGES` of `test/e2e/harness.py`, which runs the oracle of every corpus
  script on it, and `STORAGES` of `test/e2e/test_matrix.py`;
- `test_create_databases_with_a_storage_that_has_no_server`, in
  `test/test_setup_exp/test_services/test_environment_service_local.py`;
- `test_setup_with_the_file_and_sqlite_storages`, in
  `test/test_entities/test_missing_drivers.py`;
- "End-to-end oracle" in `AGENTS.md`, which names the storages.

No test fails when the last three are forgotten.

### A storage that needs a server

- `entities/<Name>Database.py`, following `entities/RedisDatabase.py`: a
  `SingletonMeta` class, the driver import guarded by an `ImportError` that
  names the extra, a probe in `__init__` that raises `server_unreachable`, and a
  method that empties the database.
- `setup_exp/services/environment_service.py`, `_initialize_storage`: prepare
  this storage there. Setup touches no server that was not selected.
- `compose.yaml`: a service with `profiles: ["<name>", "all"]`, a pinned image,
  ports bound to `127.0.0.1` (and `[::1]` when the code uses `localhost`),
  nothing persisted, and a health check.
- The driver: its pin in `pyproject.toml` and in `requirements.txt` (CI compares
  them), then `uv lock`. Add the server to `Dockerfile` and
  `speedupy_dev_env.sh`.
- `test/conftest.py`: the server in `SERVERS`, the new test files in
  `MARKER_MAP`. A new server also needs its marker in `pyproject.toml`.
- Tests that list the servers: `BACKENDS` and `ALL_DRIVER_ROOTS` in
  `test/test_entities/test_missing_drivers.py`; `CASES` in
  `test/test_entities/test_unreachable_servers.py`; in
  `test/test_setup_exp/test_services/`, the storage tuple of
  `test_create_databases_when_sqlite_database_exists_touches_no_server`
  (`test_environment_service_local.py`) and an "empties only it" test with its
  count (`test_environment_service.py`).
- `test/e2e/test_matrix_servers.py`: one row.
- `AGENTS.md`, "Safety": what setup and the tests erase.

### Contract tests

`test/test_execute_exp/test_services/test_storages/test_<Name>Storage.py`:

```python
class Test<Name>Storage(AbstractStorageTest, unittest.TestCase):
```

Implement `create_instance(serializer)`, `assert_storage_is_empty`,
`assert_cached_data(expected_data)` and
`manually_cache_a_record(func_hash, func_return, func_name=None, **kwargs)`
(`commit=True` arrives in `kwargs`). All four are `pass` in the mixin: an
assertion hook left out makes its tests pass while checking nothing. Read the
records through the driver, not through the class under test, and mutate
`save_cache_data` to see the tests fail. Override `drop_env` or `tearDown` when
the data lives outside `.speedupy/`.

Also add the name to the literal list of
`test_the_storage_names_are_the_executions` in `test/test_setup_exp/test_setup.py`.
`setup.py` takes its choices from `STORAGE_OPTIONS` by itself.

### Documents

Besides the common steps: the list of `-s` names in "Experiment Setup" of
`README.md`.

## Hash

- `execute_exp/services/hashes/<Name>Hash.py`, a subclass of `Hash` that
  implements `_hash(data: bytes) -> str`. `get_id` stays in the base class.
- There is no contract mixin. Write
  `test/test_execute_exp/test_services/test_hashes/test_<Name>Hash.py`, as
  `test_XXHashHash.py`, and fix at least one literal reference value: a digest
  that changes between releases silently empties every cache.
- Parser: the `hashes` list of `get_params()` and `hashes_msg()`.
- A native library is a maintainer decision (D3 in `RETROFIT.md`). Follow
  `native/README.md`; besides it: `PLATFORM_LIBRARIES` in `native.py`,
  `NATIVE_MAP` in `test/conftest.py`, `NATIVE_HASH_LIBRARIES` in
  `test_matrix.py`, `NATIVE_HASHES` in `test_native_loading.py` and the
  `native-platforms` floor. Never commit a binary built on your machine.

## Memory architecture

- `execute_exp/services/memory_architecures/<Name>MemArch.py` (the folder name
  is misspelled; keep it). Subclass `AbstractMemArch`, or the one-dict,
  two-dict or Memcached base whose behavior you share. The constructor takes
  `(retrieval_strategy, use_threads)`; `get_cache_entry` returns the output, not
  the `CacheData`.
- Contract tests, in `test_services/test_memory_architectures/`: inherit
  `AbstractMemArchTest`, or `AbstractOneDictMemArchTest` or
  `AbstractTwoDictMemArchTest`, before `unittest.TestCase`. Implement
  `create_instance`, `assert_cache_on_RAM_equal` and
  `insert_data_on_cache_RAM` (the last two are `pass` in the mixin). The mixin
  expects a `_thread` attribute and a `get_cache_entry` that asks the function's
  records before the single call's. `AbstractMemArchTest` leaves
  `create_cache_entry`, `save_new_cache_entries` and
  `get_new_cache_entries_size` to the subclass: test them.
- Parser: `memory_architectures` in `get_params()` and
  `memory_architecture_msg()`.
- One that needs a server follows the server list under "Storage", where it
  applies.

## Option matrix

`test/e2e/test_matrix.py` runs the oracle over a literal pairwise table.

A server storage or a Memcached architecture takes no row here (see
`test_matrix_servers.py`). For the others:

Add the name to `HASHES`, `MEM_ARCHS` or `STORAGES`. Then print the missing
rows:

```bash
(cd test/e2e && uv run python -c "
import itertools, test_matrix as m
covered = set().union(*map(m._pairs, m.PAIRWISE))
rows = [r for r in itertools.product(*m.VALUES) if not m._is_known_defect_pair(r)]
while True:
    best = max(rows, key=lambda r: len(m._pairs(r) - covered))
    if not m._pairs(best) - covered:
        break
    print(f'    {best},')
    covered |= m._pairs(best)
")
```

Append them to `PAIRWISE`, the default row staying first, and run
`uv run ruff format .`. `test_the_table_covers_every_valid_pair` checks the
result. A combination that fails because of a defect gets an `xfail` row with
its issue (`AGENTS.md`, "End-to-end oracle").

## Finish

1. `uv run pytest -q` and `uv run ruff format --check .` and
   `uv run ruff check .`. With a server backend, the run "With servers" in
   `CONTRIBUTING.md`.
2. Raise `MIN_TESTS` in `.github/workflows/ci.yml` by the rule in
   `CONTRIBUTING.md`, "Tests": in `test` and `test-servers`, and in
   `native-platforms` for a hash test. Without the servers, the count of
   `test-servers` is the count of `test` plus the deselected tests; confirm it
   in CI.
3. A design choice that outlives the pull request goes to `docs/`; a retrofit
   decision, to `RETROFIT.md`.
