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
| `entities/` | The storage backends (`Banco*.py`): SQLite, MySQL, MongoDB, Redis, Memcached, GridFS. |
| `speedupy.py` | The decorators and the entry point that the injected script imports. |
| `test/` | The tests (unittest classes, run by pytest from Task 5 on). |
| `logger/`, `util.py`, `constantes.py`, `SingletonMeta.py` | Shared helpers. |

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
- The floor is raised in the pull request that adds tests: `MIN_TESTS` in the
  `test` job of `.github/workflows/ci.yml` is the least number of tests
  (passed, skipped, xfailed and xpassed) a run may report. It is lowered only
  with the reason written in the pull request.
- CI is green at the tip of the branch. `ci-ok` is the one job that says so; it
  fails when `checks` or `test` failed or was cancelled. A job added to the
  workflow joins the `needs` of `ci-ok`.

CI runs no server: the server tests stay deselected there until Task 14.

## Safety

**The setup and the suite erase data on localhost.** On its first run,
`_create_databases` in `setup_exp/services/environment_service.py` does all of
this, whatever storage the experiment uses:

- Redis: `flushdb` on database 0 of `localhost:6379`;
- MongoDB: drops the `speedupy` databases on `localhost:27017`;
- Memcached: `flush_all` on `localhost:11211`;
- MySQL: `DROP DATABASE IF EXISTS speedupy` on `127.0.0.1` as `root`.

The storage, memory-architecture and environment tests do the same.

`uv run pytest` is safe: it deselects every test that needs a server and runs in
a scratch directory (see "Running the tests"). What is still unsafe:

- Do not run `setup_exp/setup.py`, or `SPEEDUPY_TEST_SERVERS=1 uv run pytest`,
  on a machine whose local servers hold data that matters. Until Task 13 gives
  disposable servers, use the container the `Dockerfile` builds.
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
  in `constantes.py` are relative, so changing directory is enough to move them.
  The conftest runs the session in a scratch directory.
- **Singletons are never reset:** `SingletonMeta` keeps one instance per class
  for the life of the process. `test/test_entities/test_BancoRedis.py` builds
  `BancoRedis()` under a mocked client, which then stays in the singleton.
- **Native libraries:** `MeowHash.py`, `A5Hash.py` and `MuseairBFastHash.py`
  load `libmeow.so`, `liba5hash.so` and `libmuseair.so` at import. The files are
  not versioned, no source is in the repository, and they export custom symbols
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
- **Not collected by pytest:** the modules that cannot be imported without a
  native library, listed in `NOT_COLLECTED` in `test/conftest.py`. Task 12 removes
  the list.
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

It runs the tests that need no server and no native library, in a scratch
directory, and writes nothing in the checkout (`.pytest_cache/` and
`__pycache__/` are git-ignored). Pytest's own options work (`-q`, `-k`, `-m`):
`test/conftest.py` trims `sys.argv` before any test module loads.

- **Markers.** `mysql`, `mongo`, `redis`, `memcached` and `native` come from the
  map `MARKER_MAP` in `test/conftest.py`, not from the test files. A test class
  whose fixtures touch a server is marked as a whole, even for a test that does
  not use the server. A new test file that needs a server gets its entry there.
- **Servers are opt-in.** `SPEEDUPY_TEST_SERVERS=1 uv run pytest` runs the server
  tests too. It first probes the four servers and aborts naming the unreachable
  ones: a missing server is an error, never a skip. These tests erase data (see
  "Safety") and never run in parallel. Disposable servers arrive in Task 13.
- **Native tests** are deselected until Task 12.
- `uv run pytest --collect-only -q` touches no server, whatever the variable
  says. The count by what each test needs is in `RETROFIT.md`, "Baseline".

## Retrofit

A software-engineering retrofit of this repository is in progress. Its plan, its
status table and the protocol to follow are in `RETROFIT.md`.

- When asked for the next retrofit task, in any wording or language, or asked to
  work on one, read `RETROFIT.md` and follow "Protocol" there.
- When you finish a retrofit task, tell the dev the next one without being
  asked: the task, the model, the effort, and whether to `/clear` first.
- Do not run the test suite or `setup_exp/setup.py` before reading "Safety"
  here: both erase data in the database servers on localhost.
- When a tool is missing on the machine (uv, Python, Docker, `gh`), do not
  replace it with a weaker one: follow "Tools on the dev's machine" above, which
  starts by asking the dev's go-ahead to install it.
