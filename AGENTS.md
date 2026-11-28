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
| `native/` | The native hashes (a5hash, MuseAir): the versioned binaries of five platforms, their sources as submodules, the wrappers and the build (`native/README.md`). |
| `test/` | The tests (unittest classes, run by pytest from Task 5 on). |
| `logger/`, `util.py`, `constants.py`, `SingletonMeta.py` | Shared helpers. |

## Working conventions

- **Everything versioned is in English:** code, comments, documents, issues,
  pull requests, commit messages. The conversation with the agent may be in
  Portuguese. Documents say "the maintainer", never a person's name.
- **The contribution cycle** (the issue before the code, branches, commit
  messages, what a pull request needs, the environment) is in
  [`CONTRIBUTING.md`](CONTRIBUTING.md): follow it. Create an issue only after
  asking the dev.
- **Tags are SemVer 2.0.0, with no `v`:** `X.Y.Z` (`1.7.0`), `+metadata` for a
  variant of the same version (`1.0.1+time-measure`) and `-pre` for a
  pre-release (`1.3.5-pre`). GitHub does not validate tag names on the
  organization's plan, so this line is the rule.
- **Do what the task says and nothing more.** What else you find goes to a new
  issue ("Branching model" in `CONTRIBUTING.md`).
- **Do not commit on your own.** Leave the change in the working tree and show
  the diff and the result of each check. Commit, push and the pull request are
  the dev's, or yours when the dev says so.
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

## Testing rules

The rules are in the "Tests" section of [`CONTRIBUTING.md`](CONTRIBUTING.md#tests):

- Write the tests of a region's scenarios before changing it.
- Start every bug fix with the test that reproduces the bug.
- When the tests of a region are in doubt, mutate the production code and check
  that they fail.

## Definition of done

A change is done when all of these hold:

- The tests, the format, the lint and the `MIN_TESTS` floors are as "What a
  pull request needs" and "Running locally" in `CONTRIBUTING.md` say. The lint
  rules are `[tool.ruff.lint]` in `pyproject.toml`, with no ignore left.
- CI is green at the tip of the branch. `ci-ok` is the one job that says so; it
  fails when `checks`, `security`, `test`, `test-servers` or `native-platforms`
  failed or was cancelled. A job added to the workflow joins the `needs` of
  `ci-ok`.

The `test` job runs on Linux, Windows and macOS with no server, so the server
tests stay deselected there. The `test-servers` job, on Linux only, starts the
containers of `compose.yaml` and runs them. The `native-platforms` job runs the
hash tests on Windows x64, macOS x86_64 and arm64, and Linux aarch64.

**Security checks.** CodeQL default setup, configured on GitHub and not in
`ci.yml`, analyzes `main` and the pull requests (`python`, `c-cpp`, `rust`,
`actions`). The `security` job of CI runs bandit over the tree without `test/`,
`docs/` and `native/vendor/`, blocking at medium severity and above, and
pip-audit over the exported lock, on Python 3.11. Run them locally with
the commands of that job; their tools are the `security` dependency group. A
`# nosec` names its test ID and carries its reason on the line above, and an
`--ignore-vuln` carries its reason beside the step.

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
  `__init__.py` in the current directory and remove them with `remove_paths`
  (`test/remove_paths.py`). The paths in `constants.py` are relative, so
  changing directory is enough to move them. The conftest runs the session in a
  scratch directory.
- **Windows:** the suite runs there too. Remove files with `remove_paths`, never
  with a shell command. Close a database connection before its file is removed:
  Windows does not remove an open file. SpeeduPy looks scripts up by their
  normalized path, so build such a name with `os.path.join`. A process ends its
  output lines in `\r\n`. A path written into source code is written with `!r`.
- **Singletons live as long as the process:** `SingletonMeta` keeps one instance
  per class. The autouse fixture `_restore_process_state` in `test/conftest.py`
  puts back, after every test, the instances and their attributes, `sys.argv`,
  `sys.version_info` and the current directory. It restores attributes by name,
  so an object mutated in place (a list inside a singleton) is not undone. A test
  that builds a singleton under a mock starts from no instance and says so, as
  `test_RedisDatabase.py` does.
- **Native libraries:** `A5Hash.py` and `MuseairBFastHash.py` (research
  hashes, D9) load their library on first use from `native/lib/<platform>/`,
  through `load_native_library` in `execute_exp/services/hashes/native.py`. The
  binaries are versioned for Linux x86_64 and aarch64, Windows x64 and macOS
  x86_64 and arm64. A platform without the library raises an `ImportError` that names the hash and the platform, and only that
  hash fails. Never compile a binary on your machine and commit it: only the
  workflow `native.yml` builds them, and `native/README.md` is the procedure,
  with a section for agents. A request to "update the native libraries" is
  ambiguous: ask whether it means rebuilding at the same commits or moving a
  submodule, which changes every hash value and is the maintainers' decision.
  The sources are submodules in `native/vendor/`, needed only to rebuild; a
  plain clone leaves them empty and runs every hash. The design is
  `docs/native-hashes.md`.
- **Running an experiment:** setup injects `sys.path.append(<cwd>)` and `from
  speedupy.speedupy import …` into the script, so the checkout must be
  reachable as `speedupy/` inside the experiment's directory. A script whose
  name contains `speedupy` is not treated as the user's. The default minimum
  time (`-mt`) caches nothing in a small script.
- **Server tests share state:** Redis database 0, the `speedupy` databases and
  the whole Memcached. They never run in parallel.
- **Python:** one version is supported, 3.11: see "Python versions".
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

The commands, the random order included, are in "Running locally" in
[`CONTRIBUTING.md`](CONTRIBUTING.md#running-locally).

`uv run pytest` runs the tests that need no server, in a scratch directory, and
writes nothing in the checkout (`.pytest_cache/` and `__pycache__/` are
git-ignored). Pytest's own options work (`-q`, `-k`, `-m`): `test/conftest.py`
trims `sys.argv` before any test module loads.

- **Markers.** `mysql`, `mongo`, `redis`, `memcached` and `native` come from the
  maps `MARKER_MAP` and `NATIVE_MAP` in `test/conftest.py`, not from the test
  files. A test class
  whose fixtures touch a server is marked as a whole, even for a test that does
  not use the server. A new test file that needs a server gets its entry there.
- **Servers are opt-in.** With `SPEEDUPY_TEST_SERVERS=1` a missing server is an
  error, never a skip. These tests erase data (see "Safety"): see "Running the
  tests with servers" below.
- **Native tests** run against the binaries of `native/lib/` for the running
  platform. They are skipped, with the library and the platform in the reason
  (`-rs`), only where that platform has no such library (a platform outside
  the five); anywhere else a missing or wrong binary fails. A test names its
  libraries (`a5hash`, `museair`) in `NATIVE_MAP` in `test/conftest.py`, or
  with `@pytest.mark.native("museair")`; an unknown name fails the test. The
  `native-platforms` job of CI runs the hash tests on Windows, macOS and Linux
  arm64; the `test` job runs the whole serverless suite on Linux x86_64,
  Windows x64 and macOS arm64.
- `uv run pytest --collect-only -q` touches no server, whatever the variable
  says. The count by what each test needs is in `RETROFIT.md`, "Baseline".

**The README follows the parser.** `test/test_readme.py` compares the table
under "Execution Options" of `README.md` with `build_parser()`, in both
directions: option names and accepted values. The options of the parser group
"Experimental options (beta)" stay out of the README (D8); the same test holds
the list in `docs/experimental.md` to that group.

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
`xfail(strict=True)` row whose reason names its issue (`#87`, `#88`), or a
non-strict one when the defect is intermittent (`#113`); it leaves the table
when the issue is fixed. The server storages and the Memcached
architectures are in `test/e2e/test_matrix_servers.py`, which runs only in the
server job. When an option gains or loses a value, regenerate the table (greedy,
default row first, known-defect pairs left out), review the diff, and keep
`test_the_table_covers_every_valid_pair` green.

## Blind spots of the suite

What no test executes, from the coverage report and the `# TODO: TEST` notes.
Each item has its issue: a change there is run by hand, and the pull request
says so. Reproduce the report with `uv run pytest --cov` then `uv run coverage
report` (the `test` job of CI uploads it as the `coverage` artifact). Coverage
is a report, not a gate: the floor is `MIN_TESTS`.

- **`function_calls_prov_table.py`**, 31% (#102).
- **Setup of experiments with imported scripts:** `create_experiment`, imported
  user modules and implicit `__init__.py` (#103). The oracle corpus has
  single-script experiments only.
- **Same-name nested functions** in `FunctionCalledDetectorService` (#104).
- **Server storages and the Memcached architectures** show low in the report of
  `test`; the `test-servers` job runs them. Not a blind spot of the suite.

### Experimental, outside the product's scope

Work in progress of another thesis, not part of release 2.0. The oracle and the
option matrix exercise only `manual` and `no-cache` on purpose. D8 is decided:
the feature stays in the product, off by default, and leaves no trace in the
user's scripts unless it is turned on. The switch is `--exec-mode`, in setup as
in execution (`docs/experimental.md`):

- **Setup** injects `@maybe_deterministic` only with `--exec-mode accurate`,
  `probabilistic-counting` or `probabilistic-error` (default `manual`). Every
  other step of setup is the same in every mode. It records the mode in
  `.speedupy/setup_mode.json`.
- **Execution** in an experimental mode over a `manual` or `no-cache` setup stops
  with a message (`execute_exp/services/setup_mode.py`); in `manual` and
  `no-cache` the guard reads no file, and `maybe_deterministic` is the identity
  and warns once on stderr.
- **`--help`** lists the seven options of the feature under "Experimental
  options (beta)". The mode names live in `execute_exp/parser_params.py`
  (`STABLE_EXEC_MODES`, `EXPERIMENTAL_EXEC_MODES`): one source for setup and
  execution.

- **`@maybe_deterministic` with the accurate and probabilistic execution modes**
  (and the thread retrieval mode) never runs end to end. The first call raises
  `KeyError` (#100).
- **`_execute_func_collecting_metadata`** in `speedupy.py` passes unpacked
  arguments to `_execute_func_measuring_time` and raises `TypeError` (#101).

## Running the tests with servers

Docker is needed only for this suite, the tests that need a server. Plain
`uv run pytest` needs neither a server nor Docker, and SpeeduPy itself never
needs Docker. Setup reaches a server only for the storage it is asked to
prepare (`-s`, default `file`), so an experiment that uses `file` or `sqlite`
needs none.

The commands to start the servers, run the tests and remove the servers are in
"With servers" in [`CONTRIBUTING.md`](CONTRIBUTING.md#with-servers).
`compose.yaml` starts MySQL, MongoDB, Redis and Memcached, in the versions of
the `Dockerfile`, with nothing persisted; a plain `docker compose up` starts
none.

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

## Python versions

The supported range is `requires-python` in `pyproject.toml`: today Python 3.11
only (`>=3.11,<3.12`), on Linux, Windows and macOS. A version is supported when
CI runs it in a blocking job, so the upper bound never goes beyond what CI
runs. Release 2.0 is to support Python 3.11 to 3.15 on the three systems
(decision D10, issue #128).

The range, or its floor, is stated in these places. They change together:

- `requires-python` and `[tool.ruff] target-version` (the floor) in
  `pyproject.toml`, and `uv.lock` (`uv lock`);
- `check_python_version()` in `util.py`, with its tests in `test/test_util.py`;
- `README.md` (the badge, "How to Install" and the `python3.11` of the command
  examples) and the examples of `docs/experimental.md`;
- `.python-version` (the floor) and the `Dockerfile`;
- every `python-version` of `ci.yml` and `native.yml`, and, in the `security`
  job, `uv python install` and each `--python`.

In CI, `test` runs on `ubuntu-latest`, `windows-latest` and `macos-latest`,
`test-servers` on Linux only (it needs Docker), and `native-platforms` on the
platforms of `native/lib/` that `test-servers` does not run on. The `-latest`
labels move when GitHub moves them. To run the suite on a given version without
touching `.venv`, with a version inside the range:
`uv run --isolated --locked --python 3.11 pytest`.

**Widening the range** to 3.12 to 3.15 is part 2 of Task 24. Decision D9
removed what blocked it, the pin of `mmh3`. To widen:

1. Check that every pin installs from wheels for each new version on the three
   systems. A version that needs a newer pin gets one issue per dependency, and
   one dependency is changed per step.
2. In one commit, raise the upper bound of `requires-python` and of
   `check_python_version()`, update the places above, and add a Python
   dimension to the matrix of `test`.
3. Run pip-audit once per Python for which the lock resolves differently
   (`resolution-markers` in `uv.lock`).
4. Set the floors from the counts of the new run ("Tests" in
   `CONTRIBUTING.md`).

## Formatting

ruff owns the layout (`[tool.ruff]` in `pyproject.toml`), with LF line endings
on every platform. The one commit that formatted the whole tree is listed in
`.git-blame-ignore-revs`: GitHub skips it in blame, and locally `git config
blame.ignoreRevsFile .git-blame-ignore-revs` does the same. The file names a
SHA, which constrains how a pull request is integrated: see "Branching model" in
`CONTRIBUTING.md`.

## Repository skills

Procedures that repeat, in `.claude/skills/`. A skill is a procedure, not a
logbook: it says what to do, and history stays in issues and pull requests. When
a step turns out wrong, fix the skill.

| Skill | Use it when |
| :--- | :--- |
| [`add-backend`](.claude/skills/add-backend/SKILL.md) | adding a storage, a hash or a memory architecture |
| [`safe-refactor`](.claude/skills/safe-refactor/SKILL.md) | changing code: refactoring, fix, update or feature |
| [`prove-candidate`](.claude/skills/prove-candidate/SKILL.md) | judging a suspected defect, or a change or dependency before adopting it |

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
