---
name: prove-candidate
description: Turns a candidate into a verdict with evidence, either a suspected defect (confirmed, refuted or plausible) or a change or dependency proposed for adoption (measured against criteria and recorded). Use when triaging review findings or a reported bug, before stating that something is broken, and before adopting a library, a version, an algorithm or an optimization.
---

# Proving a candidate

A candidate passed on without proof spends somebody else's time; one discarded
without proof leaves a defect or an improvement in the air.

## Verdicts

Give one per claim. A bundle of mechanism, trigger and consequence needs one for
each.

- **Confirmed:** a command or a test shows it on the current tree.
- **Refuted:** the line that makes it impossible, or a run showing it does not
  happen.
- **Plausible:** the mechanism is real and you did not confirm it. Say what
  would confirm it. Plausible measures confidence, never severity.

## Rules of proof

- **A proof without a control proves nothing.** Show that the case without the
  candidate behaves differently.
- **The path must be reachable:** find the call, the option and the condition
  that lead to it. Execute instead of deducing; an empty search is evidence only
  when the same search finds a known case.
- **Escalate by cost:** one command; then a script in a scratch directory; then
  one agent, when the exploration would flood the context.
- **Two results that disagree:** check each control before arguing.

## Running an experiment

In a new directory outside the checkout, with `<checkout>` its absolute path:

```bash
ln -s <checkout> speedupy
uv run --project <checkout> python speedupy/setup_exp/setup.py script.py
uv run --project <checkout> python script.py --exec-mode no-cache
uv run --project <checkout> python script.py -mt 0 -s file --profile
```

Mark the pure functions with `@deterministic` first. Run the last command twice:
the second run reads the cache. Setup rewrites the script. Pass `-s` to the
cached runs: execution defaults to `sqlite`, setup to `file`. Before comparing
another option, empty the cache (`rm -rf .speedupy/cache/*` with `file`) or
start a new directory, or one variant reads what the other wrote. Use `file` or
`sqlite`: setup with a server storage erases data ("Safety" in `AGENTS.md`).
Read "Reproduction traps" there before building the scenario.

## A suspected defect

1. State the claim: input or state, expected result, observed result.
2. Prove it by the rules above.
3. A confirmed one becomes a test of the project, named after the property it
   guarantees; it starts the fix (`safe-refactor`).
4. A candidate that depends on another defect splits into two.

## A change or dependency proposed for adoption

1. **Question:** what problem it solves, and what happens without it.
2. **Criteria, written before measuring,** each with the result that rejects
   the candidate. Consider:
   - the benefit, as a number (time, size, hit rate);
   - correctness: the suite and the end-to-end oracle;
   - the cache: whether keys or stored entries change;
   - Python 3.10 and 3.11 from wheels, and the platforms of `native/lib/` when
     native code is involved;
   - license, advisories (the `security` job of CI), size and upkeep.
3. **Measure the current code and the candidate** on the same machine and
   inputs, more than once, and report the spread. A difference within the
   spread is no difference. Say what was not measured.
4. **Try it without keeping it:** a throwaway branch, or a layer over the
   environment (`uv run --with "<pkg>==<version>" ...`). Check which version
   was imported. A new interpreter is an install: ask first. One dependency per
   trial.
5. **Verdict on each criterion,** then the recommendation: adopt, reject, or
   undecided with what would decide it. The decision is the maintainer's.

## Record

Whatever the outcome, with the command, the output and the control:

- the issue, or a comment in it: always;
- a decision line in `RETROFIT.md` ("Decisions already taken" or "Maintainer
  decisions"), while the retrofit runs and when it binds later tasks;
- a document in `docs/`, when the design must be explained to be kept.

A rejected candidate is recorded too, so it is not measured again.
