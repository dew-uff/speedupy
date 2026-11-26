# Experimental execution modes (beta)

SpeeduPy has three execution modes that are research in progress:
`accurate`, `probabilistic-counting` and `probabilistic-error`. They are not
recommended for general use and may return results that differ from the uncached
run. The two supported modes are `manual` (the default) and `no-cache`.

## What they are

In these modes SpeeduPy decides by itself which functions are pure. Setup marks
every function of the experiment that is not already `@deterministic` with
`@maybe_deterministic`, and at run time SpeeduPy observes each call. A function
whose calls always returned the same output (`accurate`), or whose most frequent
output reached a minimum share of the calls (`probabilistic-counting`), or whose
cached output stays within an error limit (`probabilistic-error`), is served from
the cache.

The options that apply only to them are listed under "Experimental options
(beta)" in `--help`: `--revalidation`, `--max-num-exec-til-revalidation`,
`--reduction-factor`, `--min-num-exec`, `--min-mode-occurrence`,
`--confidence-level` and `--max-error-per-function`.

## Status

The feature does not run end to end today: the first call to a
`@maybe_deterministic` function raises a `KeyError` (#100), and
`_execute_func_collecting_metadata` raises a `TypeError` (#101). The `thread`
retrieval mode is outside it (#113, #114). The test suite exercises only
`manual` and `no-cache`.

## How to turn them on

Setup and execution take the same `--exec-mode`:

```bash
python3.11 speedupy/setup_exp/setup.py --exec-mode accurate your_script.py
python3.11 your_script.py --exec-mode accurate
```

Without `--exec-mode`, setup uses `manual` and leaves no `@maybe_deterministic`
in your scripts. Setup records its mode in `.speedupy/setup_mode.json`. An
experimental run over a `manual` or `no-cache` setup stops with this message,
because no function is marked:

```text
setup was run in manual mode, so no function is marked @maybe_deterministic; run setup again with --exec-mode accurate
```

## A hand-written `@maybe_deterministic`

In `manual` and `no-cache`, `@maybe_deterministic` is ignored and the function
runs as written, so an old annotation does not break a run. SpeeduPy prints one
line to stderr, once per process, when the annotation is applied:

```text
SpeeduPy: @maybe_deterministic is ignored in manual mode; the experimental modes need setup run with the same --exec-mode (see docs/experimental.md).
```
