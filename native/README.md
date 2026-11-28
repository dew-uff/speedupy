# Native hashes: how to rebuild the binaries

The binaries of `a5hash` and `museair` are versioned in `native/lib/`, one
folder per platform, so a plain clone of SpeeduPy runs all four hashes. This
page is for the rare change that needs new binaries. The design (why the binaries are here, the platforms, the validation, the
packaging) is `docs/native-hashes.md`. Every path and command below is from
the root of the repository.

## When to rebuild

"Update the native libraries" can mean two different things. Know which one
before starting:

- **Rebuild at the same commits.** The hash values do not change. Reasons:
  - a wrapper changed (`native/src/`, `native/museair/src/lib.rs`);
  - a build file changed (`native/build.sh`, `native/build.ps1`,
    `native/museair/Cargo.toml`, `native/museair/Cargo.lock`);
  - a newer toolchain: the Rust release in
    `native/museair/rust-toolchain.toml`, or a newer runner or `manylinux`
    image, which needs no file change;
  - a platform is added.

  Follow "Procedure".
- **Move a submodule to another commit.** The hash values change, and every
  cache written before stops matching. Only the maintainers decide it, in an
  issue, before any work. MuseAir's submodule never moves to the tip: later
  versions are a different algorithm, which would be a new hash. Follow
  "Procedure", then "Moving a submodule".

Nothing else needs a rebuild. In particular, changing any Python code, the
tests or the documents does not.

## The submodules, in two minutes

A submodule is a folder of this repository that is another git repository,
pinned at one commit. `native/vendor/a5hash` and `native/vendor/museair` are
the original repositories of the two hashes. This repository stores only which
commit each one is at (`.gitmodules` holds their addresses).

A plain `git clone` leaves the two folders empty. That is enough to run and
change SpeeduPy, because the binaries are in `native/lib/`. Only a rebuild
needs the sources:

```bash
git submodule update --init        # in an existing clone: fetch the two, at the pinned commits
git clone --recurse-submodules ... # or clone with them from the start
git submodule status               # the pinned commit of each one
```

Never run `git submodule update --remote`: it moves the submodules to the tip
of their repositories, which changes the algorithms. Moving one on purpose is
"Moving a submodule".

## Procedure

Binaries are built only by the workflow `.github/workflows/native.yml`, on
GitHub's runners, never on your machine: a binary from a personal machine
cannot be traced to its toolchain. You need `git`, `gh` (logged in) and `uv`;
no compiler.

1. **Branch.** As for any task: an issue, then the branch `issue_<N>` from an
   up-to-date `main`. Fetch the submodules: `git submodule update --init`.
2. **Change** the wrapper, the build file or the submodule commit, if any.
3. **Commit and push** the change. The workflow runs on a push to any branch
   other than `main` that touches the `paths` listed at the top of
   `native.yml` (the sources, the build, the reference values, the workflow).
   For a rebuild with no file change, start it by hand on the branch:
   `gh workflow run native.yml --ref issue_<N>`.
4. **Wait for it to be green.** Each of the five platform jobs builds, then
   checks every binary against the reference values on its own system
   (`native/check.py`); a value that differs fails the job. Follow it with
   `gh run watch <run-id>`.
5. **Download the artifact** `native-binaries` of that run. It holds `lib/`
   and `manifest.json`, laid out as in `native/`. Take the run of your last
   commit, and remove the old files first, since `gh run download` does not
   overwrite:

   ```bash
   git rev-parse HEAD                                    # the commit the run must show
   gh run list --workflow native.yml --branch issue_<N> --status success \
     --json databaseId,headSha --limit 5                 # the run id of that commit
   rm -rf native/lib native/manifest.json
   gh run download <run-id> -n native-binaries -D native
   ```

6. **Check locally:** `uv run pytest`. The reference-value tests run against
   the binaries of your platform, and a test compares every file of
   `native/lib/` with the sha256 of the manifest.
7. **Commit** `native/lib/` and `native/manifest.json` together, in a commit
   of their own whose message names the run
   (`Issue(#N): Rebuild the native binaries` and the run's address). This
   commit does not start the workflow again. The `native-platforms` job of CI
   runs the hash tests on Windows, macOS and Linux arm64 with the committed
   binaries.
8. **Pull request** as usual. Say why the binaries were rebuilt; when a
   submodule moved, give the old and the new value of one reference input.

**Tests.** The reference-value tests
(`test/test_execute_exp/test_services/test_hashes/test_native_reference_values.py`)
are the test of a rebuild: they pass before it and must pass after it. A
rebuild at the same commits adds no test; a change of behaviour in a wrapper
comes with one, as any production change does (`AGENTS.md`).

## Moving a submodule

The new commit changes the values, so the workflow's check fails on every
platform and the run uploads no binary. That failure is how the new values are obtained:

1. Move the submodule and record the new commit:

   ```bash
   git -C native/vendor/<name> checkout <commit>
   git add native/vendor/<name>
   ```

   Update its commit in `native/NOTICE` and in `docs/native-hashes.md`, then
   commit and push.
2. In the failed run, each failed job prints `MISMATCH` lines and then the
   tables of the values computed on its platform, in the format of
   `test/test_execute_exp/test_services/test_hashes/native_reference_values.py`:
   `gh run view <run-id> --log-failed`.
3. Check that every failed job prints the same tables, and that only the moved
   hash changed. A platform that disagrees is a defect of the build, not a new
   value: stop there.
4. Replace the changed table in `native_reference_values.py` with the printed
   one, keep its docstring's account of where the values come from up to date,
   commit and push. The run is now green: continue at step 5 of "Procedure".
5. In the pull request, give the old and the new value of one input, and say
   that caches written with the old commit no longer hit.

The reference values change only this way, after a decision to move a
submodule. They are never edited to make a failing build pass.

## For an agent

- Ask the dev which of the two cases of "When to rebuild" is meant, unless the
  request says it. Moving a submodule needs the maintainers' decision in an
  issue first.
- The workflow runs only on a pushed commit, and `AGENTS.md` leaves commits
  and pushes to the dev: ask before the first commit and push of the branch.
- Never fix a failing check by editing the reference values or by committing
  binaries built on this machine.

## Building locally, to try a change

To see whether a change compiles before pushing, on Linux or macOS with a C
compiler and rustup:

```bash
native/build.sh macos-arm64      # or linux-x86_64, linux-aarch64, macos-x86_64
uv run python native/check.py macos-arm64
```

On Windows, from a Developer PowerShell for Visual Studio (x64):
`native/build.ps1`, then `uv run python native/check.py windows-amd64`.

These write into `native/lib/<platform>/`. Do not commit what they produce:
restore the versioned files with `git checkout native/lib` and let the
workflow build the binaries that go into the repository.
