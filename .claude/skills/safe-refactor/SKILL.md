---
name: safe-refactor
description: Changes code behind tests that were proven to fail, and compares the suite before and after. Use when refactoring, fixing a bug, updating a dependency or implementing a feature, whenever what the change did has to be separated from what was already there.
---

# Safe refactoring

The rules are "Tests" in `CONTRIBUTING.md`: tests first, a bug fix starts with
its test, and when in doubt mutate. This is how to apply them.

## 1. Declare the expected differences

Write them down before running anything. A refactoring expects none, and the
empty list is the declaration. A bug fix expects the corrected behavior and
nothing else; a feature, the new behavior. A dependency update starts with its
changelog, which says where to look.

## 2. Baseline

Run `uv run pytest` on the unchanged code, from the repository root. Keep three
things: the counts (passed, skipped, xfailed, xpassed), the duration and the
seed (`Using --randomly-seed=N` in the header, hidden by `-q`). A red baseline
is fixed first (`uv sync --locked`), or a later failure means nothing.

## 3. Map the reach

List who calls the code (search the tests too, and the target strings of
`unittest.mock.patch`). Find what no test executes:

```bash
uv run pytest --cov
uv run coverage report
```

Read "Blind spots of the suite" in `AGENTS.md`. A covered line is not a checked
line: step 5 decides that.

## 4. Cover the gaps against the current code

Write the missing tests and see them pass before the change. Written afterwards,
they only describe what you did.

## 5. Mutate

Break the production code on purpose (a sign, a boundary, a branch, a dropped
call), run the tests of the region, read the failure and undo the edit:

```bash
uv run pytest <test file> -q
```

- The red must be the expected test with the expected message. An
  `ImportError` or a `SyntaxError` is not a test catching the mutation.
- Mutate each behavior the change touches, not just one line.
- Choose test data that only the correct path satisfies.
- A mutation that stays green means a missing test: go back to step 4.
- Confirm with `git diff` that no mutation is left.

## 6. Change in small steps

One step, then the tests of the region. A change to the tests that were just
proven is a second change: do not mix it with the first.

## 7. Compare

Run the whole suite again with the baseline's seed:

```bash
uv run pytest --randomly-seed=N
```

Compare each count, not only "0 failed": fewer tests, or a new skip, is a
regression. A non-strict `xfail` (an intermittent defect) may move between
xfailed and xpassed; check its issue. Added tests shift the order, so rerun the baseline under the same
seed before blaming a new failure on the change. Every difference must be on the
list of step 1.

## 8. When the suite is not enough

- **Behavior of an experiment:** `uv run pytest test/e2e`.
- **A storage or Memcached:** "With servers" in `CONTRIBUTING.md`.
- **Hashes, serializers or storage layout:** a cache written by the old code
  must still hit with the new one. Add the old commit as a worktree outside the
  checkout (`git worktree add <old> <commit>`). Build an experiment as
  `prove-candidate` does, with `speedupy` linked to `<old>`, and run it cached
  with `-s <storage>`. Point the link at the new code
  (`ln -sfn <checkout> speedupy`) and run it again with `--profile`: every call
  is a hit. As the control, empty the cache and see the hits drop. Then
  `git worktree remove <old>`.
- **A blind spot:** run it by hand and put the command and its output in the
  pull request.
