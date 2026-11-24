"""End-to-end oracle: with the cache or without it, a script prints the same.

How to add a corpus script: see AGENTS.md, "End-to-end oracle".
"""

import pytest
from harness import (
    STORAGES,
    assert_oracle,
    corpus_scripts,
    prepare_experiment,
    run_oracle,
)


def test_corpus_has_the_starting_scripts():
    assert {"recursive.py", "std_streams.py", "kwargs_nested.py"} <= set(
        corpus_scripts()
    )


@pytest.mark.parametrize("script", corpus_scripts())
def test_setup_in_the_default_mode_leaves_no_trace_of_maybe_deterministic(
    script, tmp_path
):
    """Decision D8 (issue #118): the experimental decorator is injected only on request."""
    exp_dir = prepare_experiment(script, "file", tmp_path)

    rewritten = (exp_dir / script).read_text()

    assert "maybe_deterministic" not in rewritten
    assert "@initialize_speedupy" in rewritten


@pytest.mark.parametrize("storage", STORAGES)
@pytest.mark.parametrize("script", corpus_scripts())
def test_the_cache_changes_nothing_but_the_work_done(script, storage, tmp_path):
    assert_oracle(run_oracle(script, storage, tmp_path))
