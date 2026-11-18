"""End-to-end oracle harness: a script prints the same with the cache or without.

The harness runs one script of ``corpus/`` the way a user would. It builds a
fresh experiment directory, makes the checkout reachable there as
``speedupy/`` (setup injects ``from speedupy.speedupy import ...``), copies the
script, runs setup, then runs the script three times as a process:

1. ``--exec-mode no-cache``: the reference;
2. ``--exec-mode manual -mt 0 -s <storage>``: fills the cache;
3. the same plus ``--profile``: must be served from the cache.

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

# The block Profiler.report() prints, anchored at the end of stdout.
_PROFILER_BLOCK = re.compile(
    rb"^-+ Profiler -+\n(?P<body>.*?)^-+\n\Z", re.DOTALL | re.MULTILINE
)
_CALLS = re.compile(rb"^Number of calls to @deterministic: (\d+)$", re.MULTILINE)
_HITS = re.compile(rb"^Number of cache hits: (\d+)$", re.MULTILINE)


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


def run_oracle(script: str, storage: str, base_dir: Path) -> OracleResult:
    exp_dir = prepare_experiment(script, storage, base_dir)
    cached = [script, *CACHED_ARGS, "-s", storage]
    no_cache = _python([script, "--exec-mode", "no-cache"], exp_dir)
    first_cached = _python(cached, exp_dir)
    profiled = _python([*cached, "--profile"], exp_dir)
    second_cached, calls, hits = split_profiler_block(profiled)
    return OracleResult(no_cache, first_cached, second_cached, calls, hits)
