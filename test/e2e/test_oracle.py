"""End-to-end oracle: with the cache or without it, a script prints the same.

How to add a corpus script: see AGENTS.md, "End-to-end oracle".
"""

import pytest
from harness import STORAGES, corpus_scripts, run_oracle


def test_corpus_has_the_starting_scripts():
    assert {"recursive.py", "std_streams.py", "kwargs_nested.py"} <= set(
        corpus_scripts()
    )


@pytest.mark.parametrize("storage", STORAGES)
@pytest.mark.parametrize("script", corpus_scripts())
def test_the_cache_changes_nothing_but_the_work_done(script, storage, tmp_path):
    result = run_oracle(script, storage, tmp_path)
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
