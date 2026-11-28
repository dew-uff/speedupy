# SpeeduPy retrofit

A sequence of tasks that gives SpeeduPy the safety nets that make development
with AI agents safe: a suite anyone can run, a CI that blocks a regression,
static checks, written conventions and procedures. The model is
[noWorkflow](https://github.com/gems-uff/noworkflow): when a task says "as
noWorkflow does", read its `AGENTS.md`, `CONTRIBUTING.md`, root `conftest.py`
and `.github/workflows/ci.yml`.

This file is temporary. The last task deletes it.

## Protocol

For an agent (Claude Code) working with a dev on this repository.

### "What is the next retrofit task?"

1. Read the status table from the remote `main`, since the checkout may be
   behind: `git fetch origin`, then `git show origin/main:RETROFIT.md`. Without
   network, use the local file and say it may be out of date.
2. The next task is the first row whose state is `pending`, whose task
   dependencies are all `done`, and whose decisions (`D1`…`D11`) are answered in
   "Maintainer decisions". Name the blocked rows you passed over and what
   blocks each. A row is never passed over because of its "Who": see "Who does
   a task".
3. Check that nobody has started it: `gh issue list --state open --search
   "Retrofit T<NN> in:title"` and the same with `gh pr list`. If someone has,
   say who and move to the next row that qualifies. Without `gh`, say the check
   was skipped.
4. Answer in the dev's language, in this order: the task (number, title, one
   sentence on what it delivers), who does it and whether this dev holds that
   role, the model, the effort, whether to clear the context first, and what
   the task needs before it starts: a decision, or a tool that is missing on
   this machine (see "Tools on the dev's machine"). Give the commands to type,
   for example:

   > Next: Task 5 — pytest harness, safe by default. Who: dev, a role you
   > hold. Model: Sonnet (`/model sonnet`). Effort: high (`/effort high`).
   > Clear first: yes (`/clear`, then ask for retrofit task 5). Tools: uv is
   > not on this machine; I can install it when you say so.

   The agent cannot change the model or the effort; the dev does. If the
   session already runs the right model, say so.

### Who does a task

The "Who" column of the status table names the role a task needs on the GitHub
repository: `dev` (Write), `maintainer` (Maintain or Admin) or `admin`. The dev
at the keyboard may hold it. Read it with `gh api repos/dew-uff/speedupy --jq
.permissions`.

- **Every task is worked on in its turn, with the agent, whatever its role.**
  A `maintainer` or `admin` task is not handed to somebody else by default and
  is not skipped.
- **When the dev holds the role,** the task is theirs like any other.
- **When the dev does not,** do the part that needs no role: open the issue,
  write there what is asked, and assign it to somebody who holds the role. The
  admin tasks of the retrofit are assigned to `leomurta`. Do this when the
  task's turn comes, not before. Then have the dev give notice on the thread:
  the admin acts as soon as the notice arrives. Until then the task waits in
  its open issue, and the tasks that do not depend on it go on.
- **The thread** is the team's e-mail thread about the retrofit, which the dev
  has. Whoever is not at the keyboard is reached there: the admin, and the
  people a maintainer decision depends on. The agent sends no mail. It writes
  the message, and the dev sends it.

### Working on a task

- **One task, one issue, one branch, one pull request.** The issue is titled
  `Retrofit T<NN>: <title>`; create it when it does not exist, after asking the
  dev. The branch is `issue_<number>`, from an up-to-date `main`. Commit
  subjects start with `Issue(#<number>): `, as the history does.
- **Read the whole task first,** and the comments of its issue, where an
  earlier attempt leaves what it learned.
- **Do what the task says and nothing more.** A defect, a missing test or a
  better design found on the way goes to a new issue, mentioned in the pull
  request.
- **Do not commit on your own.** Leave the change in the working tree, show the
  diff and the result of each "Done when" check. Commit, push and the pull
  request are the dev's, or yours when the dev says so.
- **A missing tool is installed, never worked around.** The procedure is in
  "Tools on the dev's machine" below.
- **A change to production code** (anything outside `test/`, the documents and
  the tooling) comes with a test that fails before it and passes after it, and
  does not change the command line. When a task needs a product decision, the
  maintainer agrees on the solution in the issue before any code.
- **Three failed attempts at the same goal: stop, explain, recommend.** Say
  what was tried, why each attempt failed and what to change: Opus instead of
  Sonnet, or a higher effort. When the cause is not the model (a missing tool,
  the sandbox, the network, an ambiguous requirement), say that instead.
  Switching is the dev's decision.
- **A task that does not fit the quota window** stops at a state where the
  suite is as green as it was found. Write in the issue what is done and what
  is left, and tell the dev. The next session clears the context and starts
  from that comment.

### Tools on the dev's machine

Do not assume the machine has what a task needs: it probably does not.

| Tool | Needed from | For |
| :--- | :--- | :--- |
| Git and `gh` (GitHub CLI) | every task | the branch, the issue, the pull request |
| uv, and the Python it manages | Task 3 | the environment and the suite |
| Docker with Compose | Task 13 | the disposable servers |
| Nothing beyond uv and `gh` (D3) | Task 25 | the native binaries are versioned; rebuilding them runs on GitHub's runners (`native/README.md`) |

1. **Check first.** Before the first change of a task, look for each tool it
   needs and its version: `gh --version`, `uv --version`, `uv python list
   --only-installed`, `docker compose version`.
2. **Propose the install and wait.** For each missing tool, tell the dev the
   command, what it costs (disk, memory, a background virtual machine for
   Docker on macOS and Windows) and what it unlocks. Nothing is installed
   before the dev's go-ahead. That covers uv, a Python interpreter (also one
   that uv would download, as `uv sync --python`, `uv run --python` and `uv
   python install` do), Docker, `gh` and any system package. Filling `.venv`
   from `uv.lock` (`uv sync --locked`) stays inside the checkout and is not an
   install on the machine.
3. **Install it yourself when you can.** With the go-ahead, run the install and
   confirm it with the version command.
4. **When you cannot, give the dev the steps.** An install that asks for an
   administrator password, opens a graphical installer, or needs a license
   accepted or a restart is the dev's to run. Give the exact steps for the
   dev's operating system, in order, one command per line, and say how to
   confirm that each one worked. Wait, then check the version yourself before
   going on.
5. **Never trade the tool for a weaker one to avoid the install:** pip in place
   of uv, `python -m unittest` in place of pytest, a round trip through CI in
   place of local containers, a check left unrun. If the dev declines the
   install, stop, say what the task cannot deliver without it, and write that
   in the issue.

### Finishing a task

1. Run every "Done when" check and report each with its output. A check that
   was not run is reported as not run.
2. In the same pull request, set the task's row to `done (#<PR>)` and, from
   Task 1 on, update `AGENTS.md` when the task changed how to work here: a
   command, a convention, a trap.
3. Without being asked, tell the dev the next task, as in "What is the next
   retrofit task?": task, model, effort, clear first or not. A task that
   depends on this one starts after this pull request is merged.

### Model, effort and clearing the context

The team's plan offers Sonnet and Opus, with a quota counted in 5-hour windows
that Opus spends much faster. Sonnet at medium effort is the default; a task
asks for more only where its reason is written. Do not go above the task's
level on your own.

"Clear first: yes" means the task is self-contained: what it needs is in this
file, in `AGENTS.md` and in its issue, so a clean context costs less quota and
carries no stale assumption. Every task here is written that way.

## Decisions already taken

- **Tooling:** uv, `pyproject.toml`, `uv.lock`, and pytest as the runner. The
  existing unittest classes are not rewritten. `requirements.txt` stays for
  users.
- **English:** everything versioned is in English, this file included: code,
  comments, documents, issues, pull requests, commit messages. The conversation
  with the agent may be in Portuguese.
- **Production changes** are allowed when small, under the rule in "Working on
  a task".
- **Tests that need a server** are opt-in and run against disposable
  containers, never against servers that were already on the machine.
- **Existing conventions stay:** `issue_<N>` branches and the `Issue(#N): `
  prefix.
- **Tags are SemVer 2.0.0, with no `v`:** `X.Y.Z` (`1.7.0`), `+metadata` for a
  variant of the same version (`1.0.1+time-measure`) and `-pre` for a
  pre-release (`1.3.5-pre`). GitHub does not validate tag names on the
  organization's plan, so this line is the rule.
- **Documents say "the maintainer",** never a person's name.

## Safety

**The setup and the suite erase data on localhost.** On its first run,
`_create_databases` in `setup_exp/services/environment_service.py` does all of
this, whatever storage the experiment uses:

- Redis: `flushdb` on database 0 of `localhost:6379`;
- MongoDB: drops the `speedupy` databases on `localhost:27017`;
- Memcached: `flush_all` on `localhost:11211`;
- MySQL: `DROP DATABASE IF EXISTS speedupy` on `127.0.0.1` as `root`.

The storage, memory-architecture and environment tests do the same.

Until Task 5 is merged:

- Do not run the whole suite or `setup_exp/setup.py` on a machine whose local
  servers hold data that matters. Use the container the `Dockerfile` builds.
- Never run the suite from the repository root. A setup test writes and removes
  `__init__.py` in the current directory, and at the root that file is tracked.
  Today's command is `cd test && python3.10 -m unittest`.

## Baseline

Measured at commit `5c16ac1`, when this plan was written.

- **Size:** 464 tests by static count, each subclass of an abstract test mixin
  counted separately. By what they need: nothing 265, a native library 14,
  MongoDB 100, MySQL 23, Redis 23, Memcached 24, all four servers 15.
- **Run without servers** (Python 3.10, `cd test && python -m unittest`): about
  260 pass. The run does not finish: each MongoDB test waits 30 s for a
  connection.
- **Not collected:** unittest discovery skips `test/test_entities/`, which has
  no `__init__.py`.
- **Flaky:** the two tests of Task 4 failed in 10 of 20 runs each.
- **Missing:** CI, linter, formatter, lock file, license, instructions for
  agents. `main` requires a pull request with zero approvals and no status
  check. The repository is private.

## Known traps

Read from the code when the plan was written. The task that meets one confirms
it by running, and Task 1 moves the list to `AGENTS.md`.

- **argv:** `get_params()` in `execute_exp/parser_params.py` parses `sys.argv`
  the first time `SpeeduPySettings()` is built, and `speedupy.py` builds it at
  import. Under pytest, any option (`-q`, `-k`, `-m`) makes argparse exit 2.
- **The root is a package:** the repository root has an `__init__.py`. A
  `conftest.py` at the root would be imported as `speedupy.conftest` when the
  checkout directory is named `speedupy`, and `from speedupy import
  deterministic` would then fail. The conftest lives in `test/`, and `test/`
  never gains an `__init__.py`.
- **The current directory:** tests write `.speedupy/`, `script_test*.py` and
  `__init__.py` in the current directory and remove them with `rm`. The paths
  in `constantes.py` are relative, so changing directory is enough to move
  them. `test_FunctionCalledDetectorService.py` changes into its own directory
  and writes there.
- **Singletons are never reset:** `SingletonMeta` keeps one instance per class
  for the life of the process. `test/test_entities/test_BancoRedis.py` builds
  `BancoRedis()` under a mocked client, which then stays in the singleton.
- **Native libraries:** until Task 12, `MeowHash.py`, `A5Hash.py` and
  `MuseairBFastHash.py` loaded `libmeow.so`, `liba5hash.so` and
  `libmuseair.so` at import, from files that were not versioned and had no
  source in the repository. Task 12 made the loading lazy; D3 and Task 25
  (issue #112) put the sources, the build and the binaries of five platforms
  in `native/`. `AGENTS.md` has the current trap; `native/README.md` is the
  procedure to rebuild them.
- **Running an experiment:** setup injects `sys.path.append(<cwd>)` and `from
  speedupy.speedupy import …` into the script, so the checkout must be
  reachable as `speedupy/` inside the experiment's directory. A script whose
  name contains `speedupy` is not treated as the user's. The default minimum
  time (`-mt`) caches nothing in a small script.
- **Server tests share state:** Redis database 0, the `speedupy` databases and
  the whole Memcached. They never run in parallel.
- **Python:** the pinned requirements have wheels for Python 3.9 to 3.11 only.

## Maintainer decisions

Task 2 fills the "Decision" column. A task that names a decision waits for it.

| # | Question | Blocks | Decision |
| :--- | :--- | :--- | :--- |
| D1 | Open work before the format commit: PR #16 (`issue_15`) and the branch `btree-impl`. Integrate, close, or accept the rebase? | Task 9 | Close both, archived first as the tags `archive/issue_15` and `archive/btree-impl`. Task 15 reimplements the setup option on `main`, taking PR #16 as prior work; the B-tree storage is issue #34, for after the retrofit. |
| D2 | Issue #15: how should setup behave when the servers are not running? PR #16 adds `--storage` to setup. | Task 15 | Adopt issue #15 as written: setup gets `-s/--storage` with the execution's storage names, default `file`. `init_env` initializes only the chosen storage, `_env_exists` no longer requires the SQLite file, and setup never touches a server that was not selected. The disabling of `FUNCTION_CALLS_PROV` that PR #16 also did is out of scope: issue #35. |
| D3 | Where are the sources and the build commands of the three native hash libraries? | Task 25 | **Partly superseded by D9** (the six hashes no longer all stay, and MeowHash is gone). Decided by the maintainers on 2026-11-19, revised by the admin's proposal in issue #112, accepted with the merge of its pull request. The six hashes (`md5`, `murmur`, `xxhash`, `a5hash`, `meowhash`, `museair`) stay, and the three native ones run on Linux x86_64 and aarch64, Windows x64, macOS x86_64 and arm64 with no compiler on the user's machine. Their sources are git submodules of the original repositories, at the commits the measurements used (`avaneev/a5hash` `10492db`, `cmuratori/meow_hash` `b080caa`, `eternal-io/museair` `29e56ad`); the wrappers of the forks the original `.so` files came from (`JoaoLopez/a5hash` `7ff7fa3`, `JoaoLopez/meow_hash` `beeb71f`, `JoaoLopez/museair` `91e7304`) moved to `native/`. The binaries are versioned in `native/lib/`, one folder per platform, built only by a workflow, with a manifest of their sources and sha256; `native.py` loads the folder of the running platform. The 2026-11-19 version put them in a separate package, `speedupy-native` (issue #106); #112 keeps one repository and one release instead, and the native hashes stay options: a platform without a binary loses only that hash. Two limits are part of the decision: MeowHash is x86_64 with AES-NI only, since its official implementation has no ARM port, so on arm64 `-H meowhash` fails with a message that says so and the other five work; and the pinned commits are never moved silently, because MuseAir changed its algorithm across versions. Publishing on PyPI, with one wheel per platform and a generic one, is Task 27. The design is `docs/native-hashes.md`. |
| D4 | Which license, and which GitHub team or users go in `CODEOWNERS`? | Task 22 | License MIT, copyright Universidade Federal Fluminense (UFF), confirmed by the admin; `LICENSE` added in issue #68. `CODEOWNERS`: `claytonchagas` and `JoaoLopez` (`JoaoFelipe` is not an owner), confirmed on the team's thread on 2026-11-16. Task 22 adds `CODEOWNERS` with these two. |
| D5 | For this private repository: how many Actions minutes may CI spend, and are code scanning and secret scanning available on the organization's plan? | Tasks 14, 23 | Answered 2026-11-16 by the admin: the repository is public, and GitHub detects the MIT license. Tasks 14 and 23 are unblocked. |
| D6 | Which Python versions are supported? | Task 24 | **Superseded by D10.** 3.10 to 3.11: every pin installs from wheels there. 3.9 is dropped, the README says 3.10+. 3.12 and 3.13 need a newer `mmh3` pin (no wheel for 4.0.1): issue #36, outside the retrofit. `check_python_version()` is aligned in Task 24. |
| D7 | Should the server backends be optional? | Task 15 | Proposed by the maintainer and approved by the admin on 2026-11-16, as noWorkflow does. The default install (`pip install speedupy`) brings only the `file` and `sqlite` storages; each server backend is an extra (`speedupy[mysql]`, `speedupy[mongo]`, `speedupy[redis]`, `speedupy[memcached]`) plus `speedupy[all]`. Every storage imports its driver only when selected, with a clear error if it is missing. No backend discussed in a paper leaves the repository, and reproducing a paper stays one command. Task 15 implements the code part together with D2. Packaging and publishing to PyPI (extras, `CITATION.cff`, a README line `pip install speedupy[all]==X.Y.Z`) is a post-retrofit issue, to be opened later. |
| D8 | What happens to the probabilistic features (`@maybe_deterministic` and the execution modes `accurate`, `probabilistic-counting` and `probabilistic-error`), which are research in progress? | Task 15, issue #118 | Decided at the 2026-11-19 meeting, confirmed 2026-11-22. They stay in the product, off by default: no branch, no environment variable, no toggle framework. The switch is `--exec-mode`, at setup and at execution (default `manual`). Setup injects `@maybe_deterministic` only in `accurate` and `probabilistic-*` and records the mode in `.speedupy/setup_mode.json`; an experimental execution over a `manual` setup fails with a clear message. In `manual` and `no-cache`, `@maybe_deterministic` is the identity and warns once. `--help` groups the seven experimental options as "Experimental options (beta)"; the README and `docs/experimental.md` say what is experimental. The feature goes to the milestone "Experimental (thesis)", with the label `experimental`, and is promoted only in a release of its own (2.1 or 3.0). Implemented in issue #118 (PR #119). |
| D9 | Which hashes does SpeeduPy 2.0 offer? | Task 24 (part 2) | Decided 2026-11-26, endorsed by both advisors on 2026-11-26/27 (issue #156): the public hashes are `xxhash` (default, XXH3 128-bit) and `md5`. `murmur` and `meowhash` are removed with what existed only for them. BLAKE3 is evaluated in a separate issue; `a5hash` and `museair` are research items of another: they stay selectable, labelled research-grade: available and fully tested (#160). Why `murmur` (`mmh3` 4.0.1) goes: it showed no measured gain over `xxhash`, and its pin had no wheel for Python 3.12 or later (#36), which blocked Task 24 part 2. Why `meowhash` (0.5) goes: it ran on x86_64 with AES-NI only (#124), its wrapper exposed a 32-bit digest (#125), and its upstream is unmaintained since 2021 and was reclassified by its author after a published cryptanalysis. Both remain in the 1.7.x releases (tags), which the ongoing undergraduate work on MeowHash uses; 2.0 does not read 1.x caches. Supersedes D3 where it keeps the six hashes. |
| D10 | Which operating systems and Python versions does SpeeduPy 2.0 support? | Task 24 | Decided 2026-11-25. Windows, Linux and macOS, with Python 3.11 to 3.15 (`requires-python` `>=3.11,<3.16`). Supersedes D6. Part 1 (the 3.11 floor and the `test` job on the three systems) is issue #147 (PR #151); part 2 widens the range after D9. |
| D11 | What happens to the multi-thread line (cache loading in a background thread)? | Tasks 2, 21 | Decided 2026-11-26, amended by the advisors on 2026-11-26/27. The line is frozen: as measured, it does not pay off under the GIL, and its open defects (#88, #113, #114, #123, #127) are data races. The code stays in the experimental group, as beta, with no evolution; those issues carry the labels `experimental` and `frozen` in the milestone "Experimental (thesis)". The maintainers' papers do not mention it, and it is out of the text and of the replication package of the related research paper. Reopen trigger: free-threaded CPython as the default build, with numpy and pandas supporting it; it then becomes a research line of its own (parallel execution of experiments). |

## Status

| # | Task | Who | Model | Effort | Clear first | Depends on | State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Instructions for agents | dev | Sonnet | medium | yes | none | done (#32) |
| 2 | Maintainer decisions | maintainer | Sonnet | medium | yes | none | done (#<PR>) |
| 3 | uv project and lock | dev | Sonnet | low | yes | none | done (#39) |
| 4 | Fix the two flaky tests | dev | Sonnet | low | yes | 3 | done (#42) |
| 5 | pytest harness, safe by default | dev | Sonnet | high | yes | 3, 4 | done (#47) |
| 6 | CI without servers | dev | Sonnet | medium | yes | 5 | done (#49) |
| 7 | Require CI on `main` | admin | Sonnet | low | yes | 6 | done (#70) |
| 8 | Test isolation and random order | dev | Sonnet | high | yes | 6 | done (#52) |
| 9 | Format once | dev | Sonnet | low | yes | 8, D1 | done (#55) |
| 10 | Lint: automatic fixes and the gate | dev | Sonnet | medium | yes | 9 | done (#57) |
| 11 | Lint: violations that need judgment | dev | Sonnet | medium | yes | 10 | done (#59) |
| 12 | Native libraries, part 1: lazy loading | dev | Sonnet | medium | yes | 6 | done (#61) |
| 13 | Disposable servers and the first full run | dev | Opus | medium | yes | 8, 12 | done (#67) |
| 14 | CI with servers | dev | Sonnet | medium | yes | 13, D5 | done (#76) |
| 15 | Setup without servers | dev | Sonnet | medium | yes | 14, D2, D7 | done (#85) |
| 16 | End-to-end oracle: the harness | dev | Opus | medium | yes | 15 | done (#92) |
| 17 | End-to-end oracle: the option matrix | dev | Sonnet | medium | yes | 16 | done (#94) |
| 18 | English, part 1: comments and messages | dev | Sonnet | low | yes | 11 | done (#96) |
| 19 | English, part 2: identifiers and file names | dev | Sonnet | medium | yes | 17, 18 | done (#98) |
| 20 | Coverage and the blind spots of the suite | dev | Sonnet | medium | yes | 17 | done (#105) |
| 21 | README held to the tool | dev | Sonnet | medium | yes | 15 | done (#155) |
| 22 | Contribution documents | dev | Sonnet | low | yes | 14, D4 | done (#142) |
| 23 | Dependency and security checks | dev | Sonnet | medium | yes | 6, D5 | done (#133, #143) |
| 24 | Python versions | dev | Sonnet | medium | yes | 14, 23, D10 | part 1 done (#151); part 2 pending |
| 25 | Native libraries, part 2: the binaries in the repository | dev | Opus | high | yes | 14, D3 | done (#115) |
| 26 | Repository skills | dev | Sonnet | medium | yes | 19, 22 | done (#145) |
| 27 | Publish on PyPI | dev | Opus | high | yes | 21, 23, 24, 25, D7 | pending |
| 28 | Close the retrofit | dev | Sonnet | low | yes | all | pending |

**Working in parallel.** Different devs may take tasks whose dependencies are
done. The exception: Tasks 9, 10, 11, 18 and 19 rewrite many files. Start each
only when no other retrofit branch is open, and merge it before another task
starts.

## Tasks

### Task 1 — Instructions for agents

Sonnet · medium · clear first: yes · depends on: none

**Goal.** `AGENTS.md` holds what an agent must know before touching the
repository, and every session loads it.

**Why.** noWorkflow keeps its conventions, its definition of done and its traps
in `AGENTS.md`, so each session starts from them and does not rediscover them.

**Steps.**
1. Write `AGENTS.md` with these sections:
   - what SpeeduPy is and how the directories divide the work, in a few lines,
     pointing to `README.md` for usage;
   - "Working conventions": the rules of "Working on a task" and of "Tools on
     the dev's machine" above, minus what is specific to the retrofit, plus
     two rules from noWorkflow's `AGENTS.md`:
     what belongs in local memory and what belongs versioned, and retrying
     outside the sandbox when it blocks a command;
   - "Safety" and "Reproduction traps": "Safety" and "Known traps" of this
     file;
   - "Running the tests": today's only safe ways, from "Safety";
   - "Retrofit": the three bullets now in `CLAUDE.md`.
2. Replace the content of `CLAUDE.md` with `@AGENTS.md`.
3. Add `.claude/settings.json` with `{"sandbox": {"enabled": true}}` and no
   allowlist yet.
4. Point to files; do not copy versions or counts that live elsewhere.

**Done when.**
- After `/clear`, asking for the next retrofit task returns the task, model,
  effort and clear-first answer.
- Every command written in `AGENTS.md` was run in this session, or is marked as
  available from a named task on.

### Task 2 — Maintainer decisions

Sonnet · medium · clear first: yes · depends on: none · who: a maintainer

**Goal.** Each row of "Maintainer decisions" has an answer.

**Why.** Seven tasks wait for these answers, and the agent must not guess
them. The agent prepares each question and the maintainer answers it.

**Steps.**
1. For each row, gather what the repository already says and show it to the
   maintainer with the options:
   - D1: the state of PR #16 and of the branch `btree-impl` against `main`;
   - D2: issue #15 and what PR #16 changes in setup;
   - D3: every mention of the three libraries in the code, the `Dockerfile`
     and the documents;
   - D4: who holds which role on the repository;
   - D5: the organization's plan and its Actions usage, as far as the dev's
     account can see them;
   - D6: the Python range the pins install on and the one
     `check_python_version()` enforces.
2. The maintainer decides. You may say what you would choose and why; the
   table records only what the maintainer answered.
3. A decision that depends on somebody else is not deferred. The people it
   depends on are most likely on the thread (see "Who does a task"): write the
   question for the dev to send there, and record the answer when it comes.
4. Record each answer in the table and in a comment of the issue
   `Retrofit T02`. The rows are independent: an answer recorded today unblocks
   its tasks today. While one answer is awaited, record the others in a pull
   request now and that one in another.

**Done when.** No row of the table is empty.

### Task 3 — uv project and lock

Sonnet · low · clear first: yes · depends on: none · tools: uv

**Goal.** One command builds the same environment on every machine and in CI.

**Why.** noWorkflow installs from `uv.lock` with `uv sync --locked`, so a
change to the dependencies that is not locked fails before anything else runs.

**Steps.**
1. `pyproject.toml` with `[project]` (name, the version of the latest tag,
   `requires-python` for the range the pins install on, the dependencies copied
   from `requirements.txt`), `[tool.uv] package = false`, and
   `[dependency-groups] dev` with pytest and pytest-cov.
2. `uv lock`, and commit `uv.lock`.
3. A check that fails when the pins of `requirements.txt` and
   `[project.dependencies]` differ.
4. `.gitignore` gains `.venv/`.
5. Leave the `Dockerfile` working: it still installs from `requirements.txt`.

**Done when.**
- `uv lock --check` passes and `uv sync --locked` builds `.venv`.
- `uv run python -c "import numpy, scipy, mmh3, xxhash, redis, pymongo,
  pymemcache, mysql.connector, cloudpickle"` succeeds.
- The check of step 3 passes, and fails when a pin is changed on one side only.

### Task 4 — Fix the two flaky tests

Sonnet · low · clear first: yes · depends on: 3

**Goal.** The suite gives the same verdict on every run.

**The defect.**
`test_func_call_acted_as_expected_when_function_acted_as_expected_with_different_data_types`,
in `test_AccurateMode.py` and `test_ProbabilisticCountingMode.py`, pickles two
sets built separately with the same elements, one of them a `MyClass()`
instance, and expects equal bytes. Two equal sets may iterate in different
orders, so the bytes differ in about half of the runs.

**Steps.**
1. Show the failure first: run the two modules 30 times and count.
   `cd test && uv run python -m unittest <module>` is safe for these two, which
   touch no server.
2. Fix the test data so the expectation does not depend on set order.
3. Open an issue for what the test exposed in the product:
   `func_call_acted_as_expected` compares pickles, so a function that returns
   equal sets may be judged as not acting as expected. Do not fix it here.

**Done when.** 30 consecutive runs pass, the count before the fix is in the
pull request, and the issue of step 3 exists.

### Task 5 — pytest harness, safe by default

Sonnet · high · clear first: yes · depends on: 3, 4

**Goal.** From the repository root, `uv run pytest` runs every test that needs
no server and no native library, in a scratch directory, without touching
localhost servers or the checkout.

**Why.** noWorkflow's root `conftest.py` runs the suite from a scratch
directory so nothing lands in the checkout. Here it must be in place before the
first run: see "Safety". High effort because the imports, `sys.argv` and the
current directory interact; see "Known traps".

**Steps.**
1. `[tool.pytest.ini_options]`: `testpaths = ["test"]`, `pythonpath = ["."]`,
   `addopts = "--strict-markers -ra"`, and the markers `mysql`, `mongo`,
   `redis`, `memcached` and `native`.
2. `test/conftest.py`, never at the root:
   - set `sys.argv = sys.argv[:1]` at import, before any test module loads;
   - change into a fresh temporary directory for the session and back at the
     end;
   - apply the markers from a map of test paths kept in the conftest, so the
     test files stay untouched;
   - deselect the tests with a server marker unless `SPEEDUPY_TEST_SERVERS=1`;
     with it set, probe each server once at the start and abort with one
     message naming the unreachable ones: a missing server is an error, never a
     skip;
   - keep out of collection the modules that cannot be imported without a
     native library, and mark `native` the tests that fail only for that
     reason. Task 12 removes this.
3. Make `test_FunctionCalledDetectorService.py` write in the scratch directory.
4. Compare `uv run pytest --collect-only -q` per marker with "Baseline", and
   explain each difference in the pull request.
5. `.gitignore` gains `.pytest_cache/`; `.claude/settings.json` allows
   `Bash(uv run pytest *)`; "Running the tests" in `AGENTS.md` and in
   `README.md` name the one command and the opt-in variable.

**Done when.**
- `uv run pytest` from the root ends with no failure and no error, in under a
  minute with no server running. The count is in the pull request.
- `git status --short` is empty after the run, and the root `__init__.py` is
  intact.
- `uv run pytest -q -k Storage` runs: pytest's options no longer reach
  argparse.
- With `SPEEDUPY_TEST_SERVERS=1` and no server, the session aborts in seconds
  with the message.

### Task 6 — CI without servers

Sonnet · medium · clear first: yes · depends on: 5

**Goal.** Every push and pull request runs the suite, and one check says
whether it may be merged.

**Why.** noWorkflow's `ci.yml` ends in a `ci-ok` job that the ruleset of `main`
requires, and each test job has a floor, `min-tests`: a run that collects fewer
tests than before fails even when every collected test passes. That floor would
have caught `test/test_entities/` going uncollected.

**Steps.**
1. `.github/workflows/ci.yml`: triggers `push` and `pull_request`;
   `permissions: contents: read`; a newer push cancels the running workflow,
   except on `main`; actions pinned by commit SHA; `UV_MANAGED_PYTHON: "1"`.
2. Job `checks`: `uv lock --check` and the check of Task 3.
3. Job `test`, Python 3.10: `uv sync --locked`, `uv run pytest`, then the
   floor.
4. `.github/scripts/pytest-summary.sh`, adapted from noWorkflow's: writes the
   outcome to the job summary and fails when passed + skipped + xfailed +
   xpassed is below `min-tests`, or when the log has no summary line.
5. Job `ci-ok`: needs the others and fails when any failed or was cancelled.
6. `AGENTS.md` gains "Definition of done": `uv run pytest` green, the floor
   raised in the pull request that adds tests, CI green at the tip of the
   branch.

**Done when.**
- CI is green on the pull request, with the three jobs.
- The pull request shows the script exiting non-zero with a floor above the
  count.

### Task 7 — Require CI on `main`

Sonnet · low · clear first: yes · depends on: 6 · who: an admin

**Goal.** A pull request with a red `ci-ok` cannot be merged.

**Steps.**
1. Read the dev's permission: `gh api repos/dew-uff/speedupy --jq
   .permissions.admin`. The Maintain role cannot change branch protection.
2. With admin: show the dev the current protection of `main` and the change,
   and apply it on their go-ahead. Add `ci-ok` as a required status check and
   leave every other setting as it is. Protect the tags, so only a maintainer
   creates or moves one.
3. Without admin: write the change in the issue `Retrofit T07`, as a command
   and as the path in the repository settings, assign the issue and have the
   dev give notice on the thread, as "Who does a task" says. The admin applies
   the change as soon as the notice arrives. Until then the task waits in its
   open issue, and Task 8 and the others that do not depend on it go on.
4. A pull request of its own sets the row to `done`.

**Done when.** `gh api repos/dew-uff/speedupy/branches/main --jq
'.protection.required_status_checks.contexts'` lists `ci-ok`. The
`branches/main/protection` endpoint is not used here: it needs admin
permission.

### Task 8 — Test isolation and random order

Sonnet · high · clear first: yes · depends on: 6

**Goal.** No test depends on what another test left behind.

**Why.** noWorkflow runs in random order with the seed recorded, and its leak
detector fails a test that leaves process state changed. High effort because
order dependence has to be traced through the singletons.

**Known leaks, to confirm.**
- `test/test_entities/test_BancoRedis.py`: a mocked client stays in the
  `BancoRedis` singleton. Fix it before Task 13, where it would corrupt the
  Redis tests.
- `test/test_util.py`: assigns to `sys.version_info`.
- `test_DataAccess.py`: leaves mocks in `DataAccess()`.
- `test/test_speedupy_execution_modes.py`: leaves `speedupy` reloaded with
  mocked attributes.
- `test/test_setup_exp/test_setup.py`: leaves `sys.argv` changed.

**Steps.**
1. In `test/conftest.py`, a fixture around every test that restores
   `SingletonMeta._instances`, `sys.argv`, `sys.version_info` and the current
   directory.
2. Fix the tests above so each restores what it changes.
3. Add pytest-randomly to the `dev` group; `pytest-summary.sh` records the seed
   and the command that reproduces the order.
4. Run with ten seeds and fix what fails. What cannot be fixed in the session
   becomes an issue, and that module keeps a fixed order with the issue number
   beside it.

**Done when.** Ten seeds are green locally, listed in the pull request; CI is
green; the floor did not go down.

### Task 9 — Format once

Sonnet · low · clear first: yes · depends on: 8, D1

**Goal.** One formatter owns the layout, and the diff of every later task shows
only what it changed.

**Why.** noWorkflow formats with ruff, keeps LF on every platform, and lists
the format commit in `.git-blame-ignore-revs`. Today four files under
`entities/` use tabs and `BancoMemcached.py` has CRLF line endings.

**Steps.**
1. Add ruff to the `dev` group; `[tool.ruff] target-version`; `[tool.ruff.format]
   line-ending = "lf"`; `.gitattributes` with `* text=auto eol=lf`.
2. Before formatting, record the result of the suite and, for every `.py`
   file, the dump of its syntax tree.
3. `uv run ruff format .`, in one commit with nothing else.
4. Compare after: same suite counts, same syntax tree in every file, docstring
   whitespace aside.
5. A second commit adds `.git-blame-ignore-revs` with the SHA of the first, the
   CI step `ruff format --check .`, the format check in "Definition of done",
   and `Bash(uv run ruff *)` in `.claude/settings.json`.

**Done when.** `uv run ruff format --check .` is clean; the comparison of step 4
is in the pull request; `git blame --ignore-revs-file .git-blame-ignore-revs`
skips the format commit.

**Traps.** Integrate with a merge commit or a fast-forward, never a squash or a
rebase: the ignore file names a SHA. No other branch may be open (D1).

### Task 10 — Lint: automatic fixes and the gate

Sonnet · medium · clear first: yes · depends on: 9

**Goal.** `ruff check` is blocking in CI.

**Why.** noWorkflow selects `E4`, `E7`, `E9`, `F`, `W605`, `B006` and `I`, all
blocking, and leaves line length to the formatter.

**Steps.**
1. `[tool.ruff.lint] select` with that set.
2. Apply the automatic fixes (`ruff check --fix`) and run the suite. An unused
   import removed automatically may have been imported for its side effect:
   check each file whose tests change.
3. List the rules that still have violations as temporary ignores, each with
   "Task 11 removes this" on the line above.
4. Add the CI step `ruff check .` and the lint check to "Definition of done".

**Done when.** `uv run ruff check .` is clean, the suite and CI are green.

### Task 11 — Lint: violations that need judgment

Sonnet · medium · clear first: yes · depends on: 10

**Goal.** No temporary ignore is left.

**Steps.**
1. Imports after code (`E402`): in tests, delete the `sys.path` lines that
   `pythonpath` made unnecessary. In production files where the order matters
   (`speedupy.py`, `setup_exp/setup.py`), keep it with `# noqa: E402` and the
   reason on the line above.
2. Mutable default arguments (`B006`): for the ones in production code
   (`setup_exp/entities/Script.py`, `execute_exp/services/hashes/Hash.py`),
   write a test that shows state shared between calls, then fix. The
   `func_globals={}` of the test helpers is never read: the decorator removes
   it and setup injects `None`.
3. Bare `except` (`E722`): name the exception. Comparison to `None` with `==`
   (`E711`, two places): use `is`. Star import (`F403`) in
   `setup_exp/entities/FunctionGraph.py`: import the names.
4. Remove the temporary ignores of Task 10.

**Done when.** `ruff check` is clean with no temporary ignore; every `noqa` has
its reason; the suite is green and the floor covers the new tests.

### Task 12 — Native libraries, part 1: lazy loading

Sonnet · medium · clear first: yes · depends on: 6 · production change

**Goal.** A missing native library breaks only the hash that needs it.

**The defect.** Today `get_hash()` imports the three wrappers, and each loads
its `.so` at import. Without the files, `md5` cannot be selected either, and
`test_factory.py` cannot be imported.

**Steps.**
1. Write the failing test: with no `.so` present, `get_hash()` returns the
   `md5` hash.
2. Load each library on first use, with an error that names the library.
3. `.gitignore` gains `*.so`.
4. In the conftest, `native` tests skip when the library file is absent and
   fail when `SPEEDUPY_REQUIRE_NATIVE=1`. Remove the collection exclusions of
   Task 5.
5. `test_factory.py` builds a storage chosen at random. Replace it with one
   case per storage, the server ones carrying their markers.

**Done when.** `uv run pytest` is green with no `.so`; `test_factory.py` is
collected and its server-free cases run; `-rs` shows each native skip with its
reason; the floor is raised.

### Task 13 — Disposable servers and the first full run

Opus · medium · clear first: yes · depends on: 8, 12 · tools: Docker with Compose

**Goal.** One command starts throwaway servers, and every server test has a
verdict.

**Why Opus.** About 185 tests run under this harness for the first time. Each
failure has to be assigned to the test, the product or the environment, and a
wrong assignment hides a defect.

**Steps.**
1. `compose.yaml`: MySQL, MongoDB, Redis and Memcached, in the versions of the
   `Dockerfile`, with the settings of `speedupy_dev_env.sh` (Redis
   `--proto-max-bulk-len`, MySQL `--max_allowed_packet`, Memcached `-m` and
   `-I`), MySQL `root` without a password, the default ports bound to
   `127.0.0.1`, and health checks.
2. `docker compose --profile all up -d --wait`, then `SPEEDUPY_TEST_SERVERS=1 uv run pytest`.
3. For each failure: a defect of the test is fixed here; a defect of the
   product becomes an issue, and the test is marked `xfail(strict=True)` with
   the issue number; a defect of the environment is fixed in `compose.yaml`.
4. `AGENTS.md` gains "Running the tests with servers": the two commands, that
   compose refuses to start when a port is taken, which protects a server
   already on the machine, and that these tests never run in parallel.

**Done when.** The full run ends with no failure and no error, each `xfail`
listed with its issue; `docker compose --profile all down -v` leaves nothing behind; the
counts per marker are in the pull request.

### Task 14 — CI with servers

Sonnet · medium · clear first: yes · depends on: 13, D5

**Goal.** The server tests block a merge too.

**Steps.**
1. Job `test-servers`: `docker compose --profile all up -d --wait`, `SPEEDUPY_TEST_SERVERS=1
   uv run pytest`, its own `min-tests`, the compose logs uploaded on failure.
2. Add it to the `needs` of `ci-ok`.
3. D5 sets no limit on minutes (the repository is public): run it on every
   push and pull request.

**Done when.** CI is green with the job listed, and the floor is proven as in
Task 6.

### Task 15 — Setup without servers

Sonnet · medium · clear first: yes · depends on: 14, D2, D7 · production change

**Goal.** Setting up an experiment that uses SQLite or files needs no server.

**Why.** See "Safety": setup touches all four servers. Until this changes, no
end-to-end test can run on a dev's machine. D2 decides the design, and PR #16
is prior work; the command line may change here if D2 says so.

**Steps.**
1. Write the failing test: setup of a one-function script succeeds with no
   server reachable.
2. Implement what D2 decided.
3. Split `test_environment_service.py` by marker: its folder and SQLite tests
   lose the server markers.
4. Update `README.md` if an option changed.

**Done when.** The server-free run includes the environment tests that need no
server; both CI jobs are green; the floors are raised.

### Task 16 — End-to-end oracle: the harness

Opus · medium · clear first: yes · depends on: 15

**Goal.** A test holds the property that defines the tool: with the cache or
without it, a script prints and returns the same, and the second cached run
reads from the cache.

**Why.** noWorkflow's `test_oracle.py` runs each corpus script with plain
Python and under the tool, and compares. **Why Opus.** What counts as "the
same output", and what is masked, decides whether every later task can trust
the oracle.

**Steps.**
1. `test/e2e/harness.py`: builds a temporary experiment directory, makes the
   checkout reachable there as `speedupy/`, copies a corpus script, runs setup,
   then runs the script three times as a process: with `--exec-mode no-cache`,
   and twice with the cache.
2. Assert that stdout, stderr and the exit status are equal in the three runs,
   and that the third run hit the cache.
3. `test/e2e/corpus/`, three scripts to start: a recursive pure function, a
   function that writes to stdout and stderr, and a function with keyword
   arguments and nested calls.
4. Use `-mt 0`, `--exec-mode manual`, and the `sqlite` and `file` storages.
5. `AGENTS.md` says how to add a corpus script.

**Done when.**
- The tests pass locally and in CI.
- A deliberate defect is caught: make the cache return a wrong value, show the
  test failing in the pull request, and do not commit the defect.
- The floor is raised.

**Traps.** See "Running an experiment" in "Known traps". `examples/` is in
`.gitignore`, so the corpus cannot live there.

### Task 17 — End-to-end oracle: the option matrix

Sonnet · medium · clear first: yes · depends on: 16

**Goal.** Every combination of options a user can type is held by the oracle.

**Steps.**
1. In the server-free job, run the oracle over the hashes, the memory
   architectures, the retrieval strategies, the serializers and the `sqlite`
   and `file` storages.
2. In the server job, over the server storages and the Memcached
   architectures.
3. If the full product takes more than about two minutes, cover every pair of
   options instead.
4. A failing combination becomes an issue and an `xfail(strict=True)` with its
   number.

**Done when.** The matrix runs in both CI jobs; each `xfail` has its issue; the
floors are raised.

### Task 18 — English, part 1: comments and messages

Sonnet · low · clear first: yes · depends on: 11

**Goal.** No Portuguese text is left in comments, docstrings, messages and
notes.

**Steps.**
1. Translate the comments, docstrings, error messages, assertion messages and
   `TODO` notes: about 70 lines with accented characters, in `execute_exp/`
   and `test/`.
2. Before changing an error message, search for code or tests that match its
   text.
3. Remove `teste.py` from the root; if it is useful, it becomes a corpus script
   of Task 16.
4. Add a test that fails when a tracked text file contains accented
   characters, with an allowlist for what is legitimate.

**Done when.** The search for accented characters finds nothing outside the
allowlist; the suite is green. No identifier was renamed.

### Task 19 — English, part 2: identifiers and file names

Sonnet · medium · clear first: yes · depends on: 17, 18 · production change

**Goal.** No Portuguese name is left in the code.

**What changes.** `entities/Banco*.py` and their classes, `constantes.py` and
`Constantes`, `test/test_entities/test_BancoRedis.py`, and local names such as
`conexao`, `nome_banco` and `dicio`.

**Steps.**
1. Propose the table of old and new names in the issue; code starts when the
   maintainer agrees.
2. Check that no old name is persisted: a class path inside a pickle, a table
   or column, a file under `.speedupy/`. Prove it with the oracle harness: a
   store written by the commit before the rename is read by the commit after.
3. Rename, including the target strings of `unittest.mock.patch`, which no
   tool renames.
4. Extend the test of Task 18 with the old names.

**Done when.** The search for the old names finds nothing; the suite and the
oracle are green in both CI jobs; the proof of step 2 is in the pull request.

**Trap.** The misspelled packages `execute_exp/entitites` and
`execute_exp/services/memory_architecures` are not renamed here. Their paths
may be inside existing caches, so that rename needs its own issue.

### Task 20 — Coverage and the blind spots of the suite

Sonnet · medium · clear first: yes · depends on: 17

**Goal.** What no test executes is written down, each item with an issue.

**Why.** noWorkflow's `AGENTS.md` has a "Blind spots of the suite" section, so
an agent that changes one of them knows it must run it by hand and say so.

**Steps.**
1. Configure coverage as noWorkflow's `[tool.coverage.run]` does, including the
   processes the oracle starts; CI uploads the report. Coverage is not a gate:
   the floor is.
2. From the report and the `# TODO: TEST` notes, write "Blind spots of the
   suite" in `AGENTS.md`. Candidates: `@maybe_deterministic` and the
   probabilistic modes end to end, `function_calls_prov_table.py`,
   `parser_params.py`, `ZeroDictMemArch.py`.
3. Open one issue per blind spot. Include the suspected defect in
   `_execute_func_collecting_metadata` of `speedupy.py`, which unpacks the
   arguments in its call to `_execute_func_measuring_time`; give it a verdict
   with a reproduction, not by reading.

**Done when.** The report is a CI artifact; each item of the section names its
issue. Nothing is fixed here.

### Task 21 — README held to the tool

Sonnet · medium · clear first: yes · depends on: 15 · production change

**Goal.** The README cannot drift from the command line again.

**Why.** noWorkflow's `test_readme.py` holds the README to the tool. Here the
README omits storages and hashes the parser accepts.

**Steps.**
1. Split `get_params()` into a function that builds the parser and one that
   parses, with a test showing unchanged behavior.
2. Add a test that compares the option table of `README.md` with the parser,
   in both directions.
3. Bring `README.md` up to date, and list what differs between the README, the
   `Dockerfile` and `requirements.txt`: fix the documents, open issues for the
   rest.

**Done when.** The test passes, and fails when an option is deleted from the
README (shown in the pull request); the floor is raised.

**Done in #155** (issue #152). The pull request adds the README section of
#109 and closes it: the dev ran setup and an experiment with `-s redis` against
the Redis of `compose.yaml` (run 1: 42 calls, 21 hits; run 2: 4 calls, 4 hits;
21 keys in Redis; `down -v` clean). The differences left for a decision are
#150, #153 and #154.

### Task 22 — Contribution documents

Sonnet · low · clear first: yes · depends on: 14, D4

**Goal.** A new contributor, human or agent, finds the cycle and the commands
written.

**Steps.** Following noWorkflow's, write:
- `CONTRIBUTING.md`: agree on the solution in the issue before coding; the
  branching model; commit messages; what a pull request needs; the development
  environment; running locally, with and without servers;
- `.github/PULL_REQUEST_TEMPLATE.md` with the checklist, and issue templates
  for a bug and a feature;
- `.github/CODEOWNERS`, from D4; `SECURITY.md`. (`LICENSE` is already in,
  from issue #68.)

Then make `AGENTS.md` point to these files where it repeats them.

**Done when.** Every command in `CONTRIBUTING.md` was run in this session and
is listed in the pull request; no procedure is written in two places.

### Task 23 — Dependency and security checks

Sonnet · medium · clear first: yes · depends on: 6, D5

**Goal.** A vulnerable dependency or a risky call is reported by CI.

**Steps.**
1. `pip-audit` in `checks`, against the lock. An advisory that a pin keeps
   alive is listed beside the step with its reason and its issue.
2. bandit, with `[tool.bandit]`. pickle is inherent to the tool: each flagged
   site carries `# nosec` with the reason on the line above, or enters a
   baseline file with an issue.
3. `.github/dependabot.yml`, weekly, for uv and GitHub Actions, with
   `open-pull-requests-limit: 0`; a weekly scheduled run of `checks`.
4. `AGENTS.md` gains "Dependencies": one dependency per step; a major or minor
   bump is never a side effect; a Dependabot pull request is never merged as it
   stands.
5. D5 made the repository public, so code scanning and secret scanning are
   available: an admin turns them on. Open an issue for it and assign it as
   "Who does a task" says.

**Done when.** `checks` is green with each exception documented; the bandit
baseline is committed.

**Progress** (issue #128, which holds the plan in two pull requests). The task
stays pending.

- **PR 1, dependencies (#133):** `.github/dependabot.yml`.
- **PR 2, security (#143):** `usedforsecurity=False` on the two md5 calls, `# nosec`
  with its reason on the pickle imports and loads and on the two skipped MySQL
  rows, and a `security` job (bandit and pip-audit) that `ci-ok` requires.
- **bandit 1.9.4 on `daf094f`, before PR 2,** all severities. The total equals
  the 172 "security" issues that qlty.sh showed.

  | Region | High | Medium | Low | Total |
  | :--- | ---: | ---: | ---: | ---: |
  | `execute_exp/` | 1 | 3 | 4 | 8 |
  | `setup_exp/` | 1 | 0 | 0 | 1 |
  | Other production code | 0 | 0 | 0 | 0 |
  | `native/`, without `vendor/` | 0 | 0 | 3 | 3 |
  | `native/vendor/` (the two Python files, of MuseAir) | 0 | 0 | 0 | 0 |
  | `test/` | 21 | 1 | 138 | 160 |
  | **Whole tree** | **23** | **4** | **145** | **172** |

  After PR 2, the three low findings of `native/manifest.py` are what is left
  outside `test/`; the job blocks at medium and above.
- **Deferred to Task 24:** CVE-2026-114605 and CVE-2026-128089, on dnspython
  2.8.0, which only Python 3.10 uses. The job ignores both there: the fixes are
  in dnspython 2.9.x and need Python 3.11 (decision D10, in issue #128). The
  `security` group also locks filelock 4.1.0 for Python 3.10, through pip-audit.
  pip-audit reports advisories on it, fixed in 4.2.1, so Dependabot may open
  alerts. The job does not audit that group. The maintainer kept the group, and
  Task 24 is where the 3.10 pin leaves the lock.
- **Not done:** the weekly scheduled run (step 3),
  `open-pull-requests-limit: 0` (step 3), the "Dependencies" section of
  `AGENTS.md` (step 4), `[tool.bandit]` (step 2) and the issue for the admin
  (step 5). CodeQL default setup already runs; whether secret scanning is on was
  not checked. pip-audit runs in `security`, not in `checks` (step 1).

### Task 24 — Python versions

Sonnet · medium · clear first: yes · depends on: 14, 23, D10

**Goal.** The supported versions are the ones CI runs.

**Steps.**
1. Make `requires-python`, `README.md` and `check_python_version()` in
   `util.py` state the same range, from D6.
2. Add to the `test` job each version of the range that the pins install on.
3. A version that needs a newer pin gets one issue per dependency; those bumps
   are outside the retrofit.
4. `AGENTS.md` gains "Python versions", as noWorkflow's.

**Done when.** The matrix is green and the three places agree.

**Progress.** The task stays pending.

- **D10 supersedes D6** (maintainer, 2026-11-25, issue #128): SpeeduPy 2.0
  supports Windows, Linux and macOS on Python 3.11 to 3.15. D10 also brings
  Windows and macOS for the whole suite into the retrofit, which "Out of the
  retrofit" excluded.
- **Part 1, done (#151, issue #147):** the floor is 3.11 (`>=3.11,<3.12`), and
  the `test` job runs on Linux, Windows and macOS. dnspython and filelock, which
  Task 23 deferred to here, left their 3.10 versions, and the audit ignores no
  advisory.
- **Part 2, unblocked, pending:** D9 (issue #156) removed `murmur` and with it
  `mmh3`, which blocked 3.12 (#36). What is left is to widen the range to 3.12
  to 3.15, as "Python versions" in `AGENTS.md` says.

### Task 25 — Native libraries, part 2: the binaries in the repository

Opus · high · clear first: yes · depends on: 14, D3 · production change ·
done in #115 (issue #112)

**Goal.** The three native hashes run on Linux, Windows and macOS from a plain
clone, with no compiler, and their tests run in CI on the five platforms.

**Why.** D3 keeps the six hashes. Issue #112 replaced the separate
`speedupy-native` package of the first version of D3 with the binaries in this
repository; `docs/native-hashes.md` is the design.

**What was done.**
1. `native/`: the three sources as submodules of the original repositories,
   the wrappers of the forks, a MuseAir wrapper crate, `NOTICE` with the three
   licenses, and `README.md`, the procedure to rebuild the binaries.
2. `.github/workflows/native.yml` builds the binaries on the five platforms
   (Linux in a `manylinux_2_28` container), checks them against the reference
   values on each, and uploads them with `native/manifest.json` (sources,
   toolchain, platform tag, sha256).
3. The binaries and the manifest are committed in `native/lib/`.
4. `native.py` loads the folder of the running platform; a platform without a
   library raises the `ImportError` that names the hash and the platform. The
   reference values of the original `.so` files are tests through the hash
   classes; the `native` marker skips only where a platform has no such
   library.
5. CI: the `test` job runs the native tests; the `native-platforms` job runs
   the hash tests on Windows x64, macOS x86_64 and arm64 and Linux aarch64,
   and joins the `needs` of `ci-ok`. Once, the binaries were compared with
   the `speedupy-native` 0.1.0 wheels on the five platforms: all equal.

### Task 26 — Repository skills

Sonnet · medium · clear first: yes · depends on: 19, 22

**Goal.** The procedures that repeat are written where the agent finds them.

**Why.** noWorkflow keeps its procedures in `.claude/skills/`, under the rule
that a skill is a procedure, not a logbook.

**Steps.**
1. `add-backend`: adding a storage, a hash or a memory architecture, the most
   frequent change in the history. It covers the abstract class, the contract
   tests to inherit (`AbstractStorageTest`, `AbstractMemArchTest`), the
   factory, the parser, the README, the marker map, `compose.yaml` and the
   floors.
2. `safe-refactor` and `prove-candidate`, adapted from noWorkflow's.
3. `AGENTS.md` gains "Repository skills", an index.

**Done when.** Each skill was followed once in this session on a throwaway
branch and corrected where it was wrong. One skill per session is fine if the
quota is short.

### Task 27 — Publish on PyPI

Opus · high · clear first: yes · depends on: 21, 23, 24, 25, D7 · production
change

**Goal.** `pip install speedupy==X.Y.Z` installs a release from PyPI, with the
four hashes on the five platforms of `native/lib/` and the two portable ones
anywhere else.

**Why.** D7 left packaging and publishing for after the retrofit; issue #112
brought them in, since the native binaries are designed to ship in platform
wheels (`docs/native-hashes.md`, "Packaging"). Today `speedupy` cannot be
installed: `package = false`, and the code imports top-level names (`util`,
`constants`, `SingletonMeta`, `logger`, `entities`, `execute_exp`,
`setup_exp`) about 180 times.

**Steps.**
1. Move the code under one `speedupy` package and rewrite the absolute
   imports; adapt what setup injects into the user's script (`sys.path.append`
   and `from speedupy.speedupy import …`) and the oracle harness, which links
   the checkout as `speedupy/`. `package = true`.
2. The extras of D7 (`speedupy[mysql]`, `speedupy[mongo]`, `speedupy[redis]`,
   `speedupy[memcached]`, `speedupy[all]`), `CITATION.cff`, and the README
   line `pip install speedupy[all]==X.Y.Z`.
3. A script that builds one wheel per folder of `native/lib/`, with that
   folder's binaries and the platform tag the manifest gives it, plus one
   generic wheel (`py3-none-any`) with no binary; `native.py` finds the
   binaries inside the installed package. Each wheel is installed in a clean
   environment on its own platform and runs the hash tests.
4. A release workflow started by a SemVer tag (no `v`), with Trusted
   Publishing (no token stored); the first release goes to TestPyPI.
5. `AGENTS.md` gains "Releasing".

**Done when.** A tag publishes to TestPyPI; on each of the five platforms,
`pip install` of that release in a clean environment runs the four hashes, and
on another platform the generic wheel runs the two portable ones.

### Task 28 — Close the retrofit

Sonnet · low · clear first: yes · depends on: all

**Steps.**
1. Put a before-and-after table in the pull request, against "Baseline".
2. Move to `AGENTS.md` whatever in this file is still true and not yet there.
3. Delete this file and the "Retrofit" section of `AGENTS.md`.

**Done when.** A search for `RETROFIT` in the repository finds nothing.

## Out of the retrofit

Each becomes an issue when a task meets it:

- fixing the product defects the tasks find;
- renaming the misspelled packages;
- host, port and database names configurable through the environment;
- macOS and Windows for the whole suite (Task 25 covers the native hashes
  there, nothing else).
