# Native hashes: how to rebuild the binaries

The binaries of `a5hash`, `meowhash` and `museair` are versioned in `lib/`,
one folder per platform, so a plain clone of SpeeduPy runs all six hashes.
This page is for the rare change that needs new binaries. The design (why the
binaries are here, the platforms, the validation, the packaging) is
`docs/native-hashes.md`.

## When to rebuild

"Update the native libraries" can mean two different things; know which one
before starting:

- **Rebuild at the same commits** (a wrapper, a build file, a new platform, a
  newer toolchain): the hash values do not change. "Procedure" below.
- **Move a submodule to another commit:** the hash values change, and every
  cache written before stops matching. Only the maintainers decide it, in an
  issue, before any work. "Procedure" below, then "Moving a submodule".

- A wrapper changed (`src/`, `museair/src/lib.rs`).
- A build file changed (`build.sh`, `build.ps1`, `museair/Cargo.toml`,
  `museair/Cargo.lock`, `museair/rust-toolchain.toml`).
- A submodule moved to another commit. This changes the hash values, and every
  cache written before; it is a decision of the maintainers, recorded in the
  pull request, never a side effect. MuseAir's submodule never moves to the
  tip: later versions are a different algorithm, which would be a new hash.
- A platform is added.

Nothing else needs a rebuild. In particular, changing any Python code, the
tests or the documents does not.

## The submodules, in two minutes

A submodule is a folder of this repository that is another git repository,
pinned at one commit. `vendor/a5hash`, `vendor/meow_hash` and
`vendor/museair` are the original repositories of the three hashes; this
repository stores only which commit each one is at (`.gitmodules` holds their
addresses).

A plain `git clone` leaves the three folders empty. That is enough to run and
change SpeeduPy: the binaries are in `lib/`. Only a rebuild needs the
sources:

```bash
git submodule update --init        # in an existing clone: fetch the three, at the pinned commits
git clone --recurse-submodules ... # or clone with them from the start
git submodule status               # the pinned commit of each one
```

Never run `git submodule update --remote`: it moves the submodules to the tip
of their repositories, which changes the algorithms. To move one on purpose,
`cd vendor/<name> && git checkout <commit>`, then `git add vendor/<name>` in
this repository.

## Procedure

Binaries are built only by the workflow `.github/workflows/native.yml`, on
GitHub's runners, never on your machine: a binary from a personal machine
cannot be traced to its toolchain. You need `git`, `gh` (logged in) and `uv`;
no compiler.

1. **Branch.** Create the branch of your issue (`issue_<N>`) from an
   up-to-date `main`, and fetch the submodules
   (`git submodule update --init`).
2. **Change** the wrapper, the build file or the submodule commit.
3. **Push the branch.** A push to any branch other than `main` that touches
   the sources, the build, the reference values or the workflow (the `paths`
   at the top of `native.yml`) runs it. On `main`, start it by hand:
   Actions, "Native hashes", "Run workflow"
   (`gh workflow run native.yml --ref main`).
4. **Wait for it to be green.** Each of the five platform jobs builds, then
   checks every binary against the reference values on its own system
   (`check.py`); a value that differs fails the job. Follow it with
   `gh run watch`.
5. **Download the artifact** `native-binaries` of that run into `native/`. It
   holds `lib/` and `manifest.json`, laid out as in the repository:

   ```bash
   gh run list --workflow native.yml --branch issue_<N> --limit 1   # the run id
   rm -rf native/lib
   gh run download <run-id> -n native-binaries -D native
   ```

6. **Check locally:** `uv run pytest`. The reference-value tests run against
   the binaries of your platform, and a test compares every file of `lib/`
   with the sha256 of the manifest.
7. **Commit** `native/lib/` and `native/manifest.json` together, in a commit
   of their own whose message names the run
   (`Issue(#N): Rebuild the native binaries` and the run's address). The
   `native-platforms` job of CI then runs the hash tests on Windows, macOS
   and Linux arm64 with the committed binaries.
8. **Pull request** as usual. Say why the binaries were rebuilt; when a
   submodule moved, give the old and the new value of one reference input.

## Moving a submodule

The new commit changes the values, so the workflow's check fails on every
platform and uploads no binary. That failure is how the new values are
obtained:

1. Move the submodule (`cd native/vendor/<name> && git checkout <commit>`,
   then `git add native/vendor/<name>`), update its commit in `NOTICE` and in
   `docs/native-hashes.md`, and push.
2. In the failed run, each platform job prints `MISMATCH` lines and then the
   tables of the values computed there, in the format of
   `test/test_execute_exp/test_services/test_hashes/native_reference_values.py`
   (`gh run view <run-id> --log-failed`).
3. Check that the five platforms print the same tables (MeowHash only on the
   three x86_64 ones), and that only the moved hash changed. A platform that
   disagrees is a defect of the build, not a new value: stop there.
4. Replace the changed table in `native_reference_values.py` with the printed
   one, keep the docstring's account of where the values come from up to
   date, and push. The run is now green: continue at step 5 of "Procedure".
5. In the pull request, give the old and the new value of one input, and say
   that caches written with the old commit no longer hit.

The reference values change only this way, after a decision to move a
submodule. They are never edited to make a failing build pass.

## For an agent

- Ask the dev which of the two cases of "When to rebuild" is meant, unless the
  request says it; moving a submodule needs the maintainers' decision in an
  issue first.
- The workflow runs only on a pushed commit, and `AGENTS.md` leaves commits
  and pushes to the dev: ask before the first push of the branch.
- Never fix a failing check by editing the reference values or by committing
  binaries built on this machine.

## Building locally, to try a change

To see whether a change compiles before pushing, on Linux or macOS with a C
and a C++ compiler and rustup:

```bash
native/build.sh macos-arm64      # or linux-x86_64, linux-aarch64, macos-x86_64
uv run python native/check.py macos-arm64
```

On Windows, from a Developer PowerShell for Visual Studio (x64):
`native/build.ps1`, then `uv run python native/check.py windows-amd64`.

These write into `lib/<platform>/`. Do not commit what they produce: restore
the versioned files with `git checkout native/lib` and let the workflow build
the binaries that go into the repository.
