# SpeeduPy: instructions for agents

Read this before touching the repository. Usage is in `README.md`.

## What SpeeduPy is

SpeeduPy speeds up scripts by memoizing pure functions with a persistent cache.
Setup rewrites the user's script to inject the decorators; execution looks the
results up in a storage.

| Directory | Role |
| :--- | :--- |
| `setup_exp/` | Setup: reads the user's script, builds the function graph, injects the decorators. |
| `execute_exp/` | Execution: parameters, settings, hashes, memory architectures, retrieval, serializers. |
| `entities/` | The storage backends (`*Database.py`): SQLite, MySQL, MongoDB, Redis, Memcached, GridFS. |
| `speedupy.py` | The decorators and the entry point that the injected script imports. |
| `test/` | The tests (unittest classes, run by pytest from Task 5 on). |
| `logger/`, `util.py`, `constants.py`, `SingletonMeta.py` | Shared helpers. |

## Working conventions

- **Everything versioned is in English:** code, comments, documents, issues,
  pull requests, commit messages. The conversation with the agent may be in
  Portuguese. Documents say "the maintainer", never a person's name.
- **Existing conventions stay:** `issue_<N>` branches, the `Issue(#N): ` commit
  prefix, `vX.Y.Z` tags.
- **One task, one issue, one branch, one pull request.** The branch is
  `issue_<number>`, from an up-to-date `main`. Create the issue only after
  asking the dev.
- **Do what the task says and nothing more.** A defect, a missing test or a
  better design found on the way goes to a new issue, mentioned in the pull
  request.
- **Do not commit on your own.** Leave the change in the working tree and show
  the diff and the result of each check. Commit, push and the pull request are
  the dev's, or yours when the dev says so.
- **A change to production code** (anything outside `test/`, the documents and
  the tooling) comes with a test that fails before it and passes after it, and
  does not change the command line. When a task needs a product decision, the
  maintainer agrees on the solution in the issue before any code.
- **Three failed attempts at the same goal: stop, explain, recommend.** Say what
  was tried, why each attempt failed and what to change (another model, a
  higher effort). When the cause is not the model (a missing tool, the sandbox,
  the network, an ambiguous requirement), say that instead. Switching is the
  dev's decision.
- **Memory.** Before keeping a fact in memory, ask: would another agent, on
  another machine, need it? Then it is versioned, here or in the skill it
  belongs to. Keep in local memory only what dies with the machine: a local
  path, this machine's sandbox settings, the state of a session. Do not copy
  into memory what is already versioned.
- **When the sandbox blocks a command,** try again outside the sandbox. That
  triggers the permission question; the human decides.

### Tools on the dev's machine

Do not assume the machine has what a task needs.

1. **Check first.** Before the first change of a task, look for each tool and
   its version: `gh --version`, `uv --version`, `uv python list
   --only-installed`, `docker compose version`. (`uv` and `docker compose` are
   needed from Tasks 3 and 13 of the retrofit; they were not run in Task 1.)
2. **Propose the install and wait.** For each missing tool, tell the dev the
   command, what it costs (disk, memory, a background virtual machine for Docker
   on macOS and Windows) and what it unlocks. Nothing is installed before the
   dev's go-ahead. That covers uv, a Python interpreter (also one that uv would
   download), Docker, `gh` and any system package. Filling `.venv` from
   `uv.lock` stays inside the checkout and is not an install on the machine.
3. **Install it yourself when you can,** and confirm with the version command.
   An install that needs an administrator password, a graphical installer, a
   license or a restart is the dev's: give the exact steps, one command per
   line, and check the version yourself afterwards.
4. **Never trade the tool for a weaker one to avoid the install:** pip in place
   of uv, `python -m unittest` in place of pytest, a CI round trip in place of
   local containers, a check left unrun. If the dev declines, stop, say what
   cannot be delivered and write that in the issue.

## Definition of done

A change is done when all of these hold:

- `uv run pytest` is green (see "Running the tests").
- `uv run ruff format --check .` is clean. `uv run ruff format .` fixes it.
- `uv run ruff check .` is clean. The rules are `[tool.ruff.lint]` in
  `pyproject.toml`; `uv run ruff check --fix .` applies the safe fixes. There
  is no ignore left: a `# noqa` carries its reason on the line above.
- The floor is raised in the pull request that adds tests: `MIN_TESTS` in the
  `test` job (no server) and in the `test-servers` job (the whole suite) of
  `.github/workflows/ci.yml` is the least number of tests (passed, skipped,
  xfailed and xpassed) that job may report. It is lowered only with the reason
  written in the pull request.
- CI is green at the tip of the branch. `ci-ok` is the one job that says so; it
  fails when `checks`, `test` or `test-servers` failed or was cancelled. A job
  added to the workflow joins the `needs` of `ci-ok`.

The `test` job runs no server, so the server tests stay deselected there. The
`test-servers` job starts the containers of `compose.yaml` and runs them.

## Safety

**The setup with a server storage and the server suite erase data on
localhost.** On its first run in a directory, `_create_databases` in
`setup_exp/services/environment_service.py` prepares only the storage chosen
with `-s/--storage` (default `file`). The `file` and `sqlite` storages touch no
server. The others do this:

- `redis`: `flushdb` on database 0 of `localhost:6379`;
- `mongo`, `gridfs`, `mongo-file` and `mongo-gridfs`: drops the `speedupy`
  database on `localhost:27017` (they share it);
- `mysql`: `DROP DATABASE IF EXISTS speedupy`, then creates it, on `127.0.0.1`
  as `root`.

Setup never touches a server that was not selected, and never Memcached. The
storage, memory-architecture and environment tests erase all four servers.

`uv run pytest` is safe: it deselects every test that needs a server and runs in
a scratch directory (see "Running the tests"). What is still unsafe:

- Do not run `setup_exp/setup.py` with a server storage (`-s redis`, `mongo`,
  `gridfs`, `mongo-file`, `mongo-gridfs` or `mysql`), or
  `SPEEDUPY_TEST_SERVERS=1 uv run pytest`, against servers on this machine that
  hold data that matters. Run them against the disposable servers of
  `compose.yaml` (see "Running the tests with servers").
- Do not bypass the harness with `python -m unittest`. It runs every server
  test, and a setup test writes and removes `__init__.py` in the current
  directory, which at the repository root is a tracked file.

## Reproduction traps

Read from the code when the plan was written; the task that meets one confirms
it by running.

- **argv:** `get_params()` in `execute_exp/parser_params.py` parses `sys.argv`
  the first time `SpeeduPySettings()` is built, and `speedupy.py` builds it at
  import. Under pytest, any option (`-q`, `-k`, `-m`) makes argparse exit 2.
- **The root is a package:** the repository root has an `__init__.py`. A
  `conftest.py` at the root would be imported as `speedupy.conftest` when the
  checkout directory is named `speedupy`, and `from speedupy import
  deterministic` would then fail. The conftest lives in `test/`, and `test/`
  never gains an `__init__.py`. Left alone, pytest also makes the root a
  `Package`: its setup prepends the parent of the checkout to `sys.path`, and
  `importlib.reload(speedupy)` then reloads the empty `speedupy/__init__.py`
  instead of `speedupy.py`. The conftest collects the root as a plain directory.
- **The current directory:** tests write `.speedupy/`, `script_test*.py` and
  `__init__.py` in the current directory and remove them with `rm`. The paths
  in `constants.py` are relative, so changing directory is enough to move them.
  The conftest runs the session in a scratch directory.
- **Singletons live as long as the process:** `SingletonMeta` keeps one instance
  per class. The autouse fixture `_restore_process_state` in `test/conftest.py`
  puts back, after every test, the instances and their attributes, `sys.argv`,
  `sys.version_info` and the current directory. It restores attributes by name,
  so an object mutated in place (a list inside a singleton) is not undone. A test
  that builds a singleton under a mock starts from no instance and says so, as
  `test_RedisDatabase.py` does.
- **Native libraries:** `MeowHash.py`, `A5Hash.py` and `MuseairBFastHash.py`
  load `libmeow.so`, `liba5hash.so` and `libmuseair.so` on first use, through
  `load_native_library` in `execute_exp/services/hashes/native.py`; a missing
  file raises an `ImportError` that names it, and only that hash fails. The
  files are git-ignored (`*.so`), no source is in the repository, and they export custom symbols
  (`MeowHash_32`, `GetMeowDefaultSeed`, `a5hash_128_64`, `museair_bfast_64`).
- **Running an experiment:** setup injects `sys.path.append(<cwd>)` and `from
  speedupy.speedupy import …` into the script, so the checkout must be
  reachable as `speedupy/` inside the experiment's directory. A script whose
  name contains `speedupy` is not treated as the user's. The default minimum
  time (`-mt`) caches nothing in a small script.
- **Server tests share state:** Redis database 0, the `speedupy` databases and
  the whole Memcached. They never run in parallel.
- **Python:** the pinned requirements have wheels for Python 3.9 to 3.11 only.
  `.python-version` pins 3.10, the version CI uses, because two tests in
  `test_serializers/test_util.py` compare Python 3.10 bytecode and fail on 3.11.
- **Not collected by unittest:** unittest discovery skips `test/test_entities/`,
  which has no `__init__.py`. pytest collects it.
- **Unraisable warnings:** the server storage tests define `__del__` that reads
  `self.mongo`, which exists only after `setUp`. pytest builds every test case
  object, so the deselected ones print `PytestUnraisableExceptionWarning`. It is
  noise, not a failure.
- **Sets of objects:** two sets built separately that hold distinct instances
  of a class without `__hash__` iterate in an order that depends on the ids, so
  their pickles differ. Share the instance in test data (Task 4).

## Running the tests

From the repository root, one command:

```bash
uv run pytest
```

It runs the tests that need no server (the native ones skip without the `.so` files), in a scratch
directory, and writes nothing in the checkout (`.pytest_cache/` and
`__pycache__/` are git-ignored). Pytest's own options work (`-q`, `-k`, `-m`):
`test/conftest.py` trims `sys.argv` before any test module loads.

- **Random order.** pytest-randomly shuffles the tests and prints its seed in the
  header (`Using --randomly-seed=N`); the job summary of CI records it. To
  rerun an order: `uv run pytest --randomly-seed=N`. A test that
  passes only in a fixed order is a bug in the test: fix it, or open an issue
  and note the number beside the module.

- **Markers.** `mysql`, `mongo`, `redis`, `memcached` and `native` come from the
  maps `MARKER_MAP` and `NATIVE_MAP` in `test/conftest.py`, not from the test
  files. A test class
  whose fixtures touch a server is marked as a whole, even for a test that does
  not use the server. A new test file that needs a server gets its entry there.
- **Servers are opt-in.** `SPEEDUPY_TEST_SERVERS=1 uv run pytest` runs the server
  tests too. It first probes the four servers and aborts naming the unreachable
  ones: a missing server is an error, never a skip. These tests erase data (see
  "Safety") and never run in parallel. Run them against the disposable
  servers: see "Running the tests with servers" below.
- **Native tests** need the `.so` files and are skipped, with the missing file
  in the reason (`-rs`), when they are absent. `SPEEDUPY_REQUIRE_NATIVE=1` makes
  a missing file a failure. A test names its libraries in `NATIVE_MAP` in
  `test/conftest.py`, or with `@pytest.mark.native("libmeow.so")`. The files
  are built from Task 25 on.
- `uv run pytest --collect-only -q` touches no server, whatever the variable
  says. The count by what each test needs is in `RETROFIT.md`, "Baseline".

## End-to-end oracle

`test/e2e/test_oracle.py` holds the property that defines the tool: with the
cache or without it, a script prints and returns the same. For each script of
`test/e2e/corpus/` and each of the `sqlite` and `file` storages,
`test/e2e/harness.py` builds an experiment directory in `tmp_path`, links the
checkout there as `speedupy/`, runs setup, then runs the script three times:
`--exec-mode no-cache`, then twice with `--exec-mode manual -mt 0 -s
<storage>`, the last one with `--profile`.

- **The same output** is stdout, stderr and the exit status, byte for byte,
  each stream on its own (their interleaving is not compared). The only
  masking is the Profiler block at the end of the third run's stdout. Every
  call that reaches `@deterministic` in the third run must be a cache hit.
- **`DEBUG` is removed** from the scripts' environment (it prints to stdout).
  `PYTHONHASHSEED` is not fixed.

To add a corpus script:

1. Put a script in `test/e2e/corpus/`, with a `main()` called under `if
   __name__ == "__main__":`. Its name does not contain `speedupy` or start
   with `test_`.
2. Mark its pure functions with `@deterministic` (`from speedupy.speedupy
   import deterministic`); setup adds the rest. At least one call must reach a
   `@deterministic` function.
3. Its output must not change from one plain run to the next: no time, no
   random numbers without a seed, no ids, no iteration over sets. When it
   needs a server or a native library, it is not a corpus script of this
   test: open an issue.
4. `uv run pytest test/e2e` picks it up, two tests more: raise both
   `MIN_TESTS` floors in `.github/workflows/ci.yml`.

The harness runs in a few seconds per script. A corpus script that fails
because of a defect of SpeeduPy is not added until the defect is fixed; it
goes in the defect's issue.

**The option matrix.** `test/e2e/test_matrix.py` runs the oracle over the
options a user can type (hash, memory architecture, retrieval strategy and
execution mode, serializer, storage) as a pairwise covering array, a literal
table with the default combination first. A combination that fails today is a
`xfail(strict=True)` row whose reason names its issue (`#87`, `#88`); it leaves
the table when the issue is fixed. The server storages and the Memcached
architectures are in `test/e2e/test_matrix_servers.py`, which runs only in the
server job. When an option gains or loses a value, regenerate the table (greedy,
default row first, known-defect pairs left out), review the diff, and keep
`test_the_table_covers_every_valid_pair` green.

## Running the tests with servers

Docker is needed only for this suite, the tests that need a server. Plain
`uv run pytest` needs neither a server nor Docker, and SpeeduPy itself never
needs Docker. Setup reaches a server only for the storage it is asked to
prepare (`-s`, default `file`), so an experiment that uses `file` or `sqlite`
needs none.

From the repository root, two commands:

```bash
docker compose up -d --wait
SPEEDUPY_TEST_SERVERS=1 uv run pytest
```

`compose.yaml` starts MySQL, MongoDB, Redis and Memcached, in the versions of
the `Dockerfile`, with nothing persisted; `--wait` returns when their health
checks pass. `docker compose down -v` removes them and leaves nothing behind.

- **A server already on the machine is protected.** The ports are the default
  ones, bound to the loopback only, and compose refuses to start when one is
  taken. Stop the local server first; never point the tests at it.
- **Never in parallel.** The tests share Redis database 0, the `speedupy`
  databases and the whole Memcached: one run at a time, and no `-n`.
- **`localhost` may be `::1`.** The code reaches MongoDB, Redis and Memcached
  as `localhost`, and pymemcache tries only the first address it resolves to,
  so those three are bound to `[::1]` too.
- **MongoDB needs file descriptors.** A run opens about 750 connections, more
  than the container's default limit of 1024; `compose.yaml` sets 64000, as
  MongoDB recommends.
- **Memcached in a test:** pymemcache writes with `noreply` by default, so a
  read through another client may overtake a write, and `flush_all` hides the
  items at once but `curr_items` drops only later. Read the keys back; do not
  count them with `stats()`.

## Formatting

ruff owns the layout (`[tool.ruff]` in `pyproject.toml`), with LF line endings
on every platform. The one commit that formatted the whole tree is listed in
`.git-blame-ignore-revs`: GitHub skips it in blame, and locally `git config
blame.ignoreRevsFile .git-blame-ignore-revs` does the same. The file names a
SHA, so a pull request is integrated with a merge commit or a fast-forward,
never a squash or a rebase.

## Retrofit

A software-engineering retrofit of this repository is in progress. Its plan, its
status table and the protocol to follow are in `RETROFIT.md`.

- When asked for the next retrofit task, in any wording or language, or asked to
  work on one, read `RETROFIT.md` and follow "Protocol" there.
- When you finish a retrofit task, tell the dev the next one without being
  asked: the task, the model, the effort, and whether to `/clear` first.
- Do not run the server suite (`SPEEDUPY_TEST_SERVERS=1`) or `setup_exp/setup.py`
  with a server storage before reading "Safety" here: both erase data in the
  database servers on localhost.
- When a tool is missing on the machine (uv, Python, Docker, `gh`), do not
  replace it with a weaker one: follow "Tools on the dev's machine" above, which
  starts by asking the dev's go-ahead to install it.
