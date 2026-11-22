"""Check that setup ran in the execution mode the experiment is run in (issue #118).

Setup marks functions with @maybe_deterministic only for the experimental
execution modes, so an experimental run over a ``manual`` or ``no-cache`` setup
would silently behave as ``manual``. Setup records its mode in a small JSON file;
this check reads it.
"""

import json
import os

from constants import Constants
from execute_exp.parser_params import EXPERIMENTAL_EXEC_MODES, STABLE_EXEC_MODES


def check_setup_mode(exec_mode: str) -> None:
    """Raise RuntimeError when an experimental run follows a manual or no-cache setup.

    In ``manual`` and ``no-cache`` it returns at once and touches no file. A
    missing or unreadable record (a setup made before it existed) lets the run go on.
    """
    if exec_mode not in EXPERIMENTAL_EXEC_MODES:
        return
    setup_mode = _read_setup_mode()
    if setup_mode in STABLE_EXEC_MODES:
        raise RuntimeError(
            f"setup was run in {setup_mode} mode, so no function is marked "
            f"@maybe_deterministic; run setup again with --exec-mode {exec_mode}"
        )


def _read_setup_mode():
    filename = Constants().EXP_SETUP_MODE_FILENAME
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, "r") as file:
            return json.load(file).get("exec_mode")
    except (OSError, ValueError, AttributeError):
        return None
