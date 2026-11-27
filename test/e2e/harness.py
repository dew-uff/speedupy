"""End-to-end oracle harness: a script prints the same with the cache or without.

The harness runs one script of ``corpus/`` the way a user would. It builds a
fresh experiment directory, makes the checkout reachable there as
``speedupy/`` (setup injects ``from speedupy.speedupy import ...``), copies the
script, runs setup, then runs the script three times as a process:

1. ``--exec-mode no-cache``: the reference;
2. ``--exec-mode manual -mt 0 -s <storage>``: fills the cache;
3. the same plus ``--profile``: must be served from the cache.

``test_oracle.py`` runs the defaults; ``test_matrix.py`` adds the options a
user can type (hash, memory architecture, retrieval, serializer) to runs 2 and 3.

What counts as "the same output" (issue #90):

- stdout, stderr and the exit status, compared byte for byte. The two streams
  are captured apart, so how their lines interleave is not compared:
  SpeeduPy itself captures them apart.
- The only masking: the Profiler block that ``--profile`` prints at the very
  end of the stdout of run 3 is cut off before the comparison, and parsed to
  count the cache hits.
- The environment is inherited, except ``DEBUG``: ``DEBUG=True`` prints log
  lines to stdout. ``PYTHONHASHSEED`` is left alone, so a cache key that
  depends on it shows up as a miss.
"""

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

CHECKOUT = Path(__file__).resolve().parents[2]
CORPUS_DIR = Path(__file__).resolve().parent / "corpus"
STORAGES = ("sqlite", "file")
TIMEOUT_SECONDS = 120

CACHED_ARGS = ("--exec-mode", "manual", "-mt", "0")

# The block Profiler.report() prints, anchored at the end of stdout. Its lines
# end in "\r\n" on Windows.
_PROFILER_BLOCK = re.compile(
    rb"^-+ Profiler -+\r?\n(?P<body>.*?)^-+\r?\n\Z", re.DOTALL | re.MULTILINE
)
_CALLS = re.compile(rb"^Number of calls to @deterministic: (\d+)\r?$", re.MULTILINE)
_HITS = re.compile(rb"^Number of cache hits: (\d+)\r?$", re.MULTILINE)


@dataclass(frozen=True)
class Run:
    args: tuple
    returncode: int
    stdout: bytes
    stderr: bytes

    def describe(self) -> str:
        return (
            f"args={list(self.args)} returncode={self.returncode}\n"
            f"--- stdout ---\n{self.stdout.decode(errors='replace')}"
            f"--- stderr ---\n{self.stderr.decode(errors='replace')}"
        )


@dataclass(frozen=True)
class OracleResult:
    no_cache: Run
    first_cached: Run
    # Run 3 with its Profiler block cut off.
    second_cached: Run
    deterministic_calls: int
    cache_hits: int


def corpus_scripts() -> list:
    return sorted(p.name for p in CORPUS_DIR.glob("*.py"))


def _env() -> dict:
    env = dict(os.environ)
    env.pop("DEBUG", None)
    return env


def _python(args, cwd: Path) -> Run:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        env=_env(),
        capture_output=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )
    return Run(tuple(args), completed.returncode, completed.stdout, completed.stderr)


def prepare_experiment(script: str, storage: str, base_dir: Path) -> Path:
    """Build the experiment directory and run setup in it."""
    if "speedupy" in script:
        raise ValueError(f"{script}: setup ignores a script named *speedupy*")
    exp_dir = base_dir / "experiment"
    exp_dir.mkdir()
    (exp_dir / "speedupy").symlink_to(CHECKOUT, target_is_directory=True)
    shutil.copyfile(CORPUS_DIR / script, exp_dir / script)
    setup = _python(["speedupy/setup_exp/setup.py", "-s", storage, script], exp_dir)
    if setup.returncode != 0:
        raise AssertionError(f"setup failed:\n{setup.describe()}")
    return exp_dir


def split_profiler_block(run: Run) -> tuple:
    """Return run 3 without its Profiler block, and the (calls, hits) it reports."""
    match = _PROFILER_BLOCK.search(run.stdout)
    if match is None:
        raise AssertionError(
            f"no Profiler block at the end of stdout:\n{run.describe()}"
        )
    body = match.group("body")
    calls, hits = _CALLS.search(body), _HITS.search(body)
    if calls is None or hits is None:
        raise AssertionError(f"Profiler block without the counts:\n{run.describe()}")
    stripped = Run(run.args, run.returncode, run.stdout[: match.start()], run.stderr)
    return stripped, int(calls.group(1)), int(hits.group(1))


def run_oracle(
    script: str, storage: str, base_dir: Path, options: tuple = ()
) -> OracleResult:
    """Run the three runs; ``options`` are extra arguments of the two cached runs."""
    exp_dir = prepare_experiment(script, storage, base_dir)
    cached = [script, *CACHED_ARGS, "-s", storage, *options]
    no_cache = _python([script, "--exec-mode", "no-cache"], exp_dir)
    first_cached = _python(cached, exp_dir)
    profiled = _python([*cached, "--profile"], exp_dir)
    second_cached, calls, hits = split_profiler_block(profiled)
    return OracleResult(no_cache, first_cached, second_cached, calls, hits)


def assert_oracle(result: OracleResult) -> None:
    """The property of the tool: the same output, and run 3 served by the cache."""
    reference = result.no_cache
    for name, run in (("run 2", result.first_cached), ("run 3", result.second_cached)):
        context = (
            f"\nrun 1 (no-cache):\n{reference.describe()}\n{name}:\n{run.describe()}"
        )
        assert run.stdout == reference.stdout, f"{name}: stdout differs{context}"
        assert run.stderr == reference.stderr, f"{name}: stderr differs{context}"
        assert run.returncode == reference.returncode, (
            f"{name}: exit status differs{context}"
        )

    # Every call that reaches @deterministic in run 3 is served from the cache.
    assert result.deterministic_calls > 0, result.second_cached.describe()
    assert result.cache_hits == result.deterministic_calls, (
        f"run 3: {result.cache_hits} cache hits for "
        f"{result.deterministic_calls} calls to @deterministic"
    )
