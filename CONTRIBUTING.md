# Contributing to SpeeduPy

How a change gets from an idea to `main`. Using SpeeduPy is in
[`README.md`](README.md); what an agent must also know before touching the
repository is in [`AGENTS.md`](AGENTS.md).

Everything versioned is in English: code, comments, documents, issues, pull
requests and commit messages.

## Before coding: agree on the solution in the issue

Every change starts with an issue. Before writing code, write the proposed
solution there: what changes, how it behaves and which questions are open. When
the change needs a product decision, the maintainer agrees on the solution in
the issue first. Decisions taken later, during the review, go back to the issue
as a comment.

## Branching model

- One issue, one branch, one pull request.
- The branch is `issue_<N>`, where `N` is the number of the issue, created from
  an up-to-date `main`.
- A defect, a missing test or a better design found on the way goes to a new
  issue, mentioned in the pull request.
- Pull requests are integrated with merge commits only, never a squash or a
  rebase: `.git-blame-ignore-revs` names commits by their SHA.
- Never force-push.

## Commit messages

Write them in English and start the subject with `Issue(#N): `, using the number
of the branch's issue:

```
Issue(#128): Add dependabot.yml for uv and GitHub Actions updates
```

## What a pull request needs

- **The issue it closes:** `Closes #N` in the description.
- **Tests,** following the rules in [Tests](#tests). A change to production code
  (anything outside `test/`, the documents and the tooling) comes with a test
  that fails before it and passes after it, and does not change the command line.
- **CI green** at the tip of the branch: the `ci-ok` check passes.
- **A higher floor when tests are added.** `MIN_TESTS`, in
  `.github/workflows/ci.yml`, is the least number of tests (passed, skipped,
  xfailed and xpassed) a job may report. Raise it in the `test` job (no server)
  and in the `test-servers` job (the whole suite) and, for hash tests, in the
  `native-platforms` job. It is lowered only with the reason written in the pull
  request.
- **Clean format and lint** (see [Running locally](#running-locally)). A
  `# noqa` carries its reason on the line above.
- **The output before and after,** when behavior changes.
- **The server tests run,** when a storage changes (see
  [With servers](#with-servers)).
- **Updated documents,** when what they describe changes.
- **A manual run,** when the change touches code that no test executes: see
  "Blind spots of the suite" in [`AGENTS.md`](AGENTS.md).

## Tests

1. **Tests first.** Before changing a region of the code, write the tests that
   cover that region's scenarios, then change it.
2. **A bug fix starts with its test.** Write the test that reproduces the bug;
   the fix makes it pass.
3. **When in doubt, mutate.** When the tests of a region are in doubt, mutate the
   production code on purpose (a sign, a boundary, a branch) and check that the
   tests fail. Improve them until they do. Do not commit the mutation.

Coverage is a report, not a target: it rises as a consequence of these rules.

Each `MIN_TESTS` floor in `.github/workflows/ci.yml` is set to the collected
count of its job (passed, skipped, xfailed and xpassed) minus 2. A job with a
matrix has one floor for all its legs: the lowest count among them minus 2.

## Development environment

- **Git.**
- **[uv](https://docs.astral.sh/uv/),** which creates `.venv` from `uv.lock` and
  runs every tool.
- **Python,** in the version that `.python-version` names. uv downloads it when
  the machine does not have it.
- **Docker with Compose,** only for the tests that need a server.

```bash
git clone https://github.com/dew-uff/speedupy.git
cd speedupy
uv sync --locked
```

`--locked` installs exactly what `uv.lock` says, and fails when the lock and
`pyproject.toml` disagree.

## Running locally

All commands run from the repository root.

### Without servers

```bash
uv run pytest -q                  # the tests that need no server
uv run pytest test/e2e            # the end-to-end oracle and the option matrix
uv run ruff format --check .      # format check
uv run ruff format .              # format
uv run ruff check .               # lint
uv run ruff check --fix .         # apply the safe lint fixes
```

The tests run in a scratch directory and in a random order. A run without `-q`
prints the seed in its header (`Using --randomly-seed=N`), and the job summary of
CI records it. To rerun an order:

```bash
uv run pytest --randomly-seed=N
```

A test that passes only in a fixed order is a bug in the test: fix it, or open
an issue and note its number beside the module.

Do not run the tests with `python -m unittest`: it bypasses the safeguards of
`test/conftest.py` and runs the tests that erase server data. How to add a script
to the end-to-end oracle is in [`AGENTS.md`](AGENTS.md).

### With servers

**These tests erase data** on the MySQL, MongoDB, Redis and Memcached servers on
localhost (see "Safety" in [`AGENTS.md`](AGENTS.md)). Run them against the
disposable servers of `compose.yaml`:

```bash
docker compose --profile all up -d --wait
SPEEDUPY_TEST_SERVERS=1 uv run pytest -q
docker compose --profile all down -v
```

The first command returns when the four servers are healthy; the last removes
them and leaves nothing behind. Compose refuses to start when a port is taken,
which protects a server already on the machine: stop it first, and never point
the tests at it. The tests share state in the servers, so run one at a time and
without `-n`.

Each server (`mysql`, `mongo`, `redis`, `memcached`) also has a profile of its
own, to start only that one:

```bash
docker compose --profile redis up -d --wait
```

The test run with `SPEEDUPY_TEST_SERVERS=1` needs all four: it stops at the
start and names the ones it cannot reach.

## Security

Do not report a vulnerability in a public issue: see
[`SECURITY.md`](SECURITY.md).
