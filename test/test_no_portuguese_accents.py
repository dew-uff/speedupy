"""Guard for Task 18: no accented letters (Portuguese text) in tracked text files."""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Latin-1 and Latin Extended-A letters with diacritics (written as escapes so
# this file stays ASCII). Typographic punctuation such as dashes, arrows and
# curly quotes is legitimate and not matched.
ACCENTED = re.compile("[À-ÖØ-öø-ſ]")

# path -> reason the accented letters are legitimate. Empty on purpose.
ALLOWLIST: dict[str, str] = {}


def _tracked_files():
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    return [p for p in out.decode().split("\0") if p]


def test_no_accented_letters_in_tracked_text_files():
    try:
        files = _tracked_files()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("not a git checkout")
    found = []
    for name in files:
        if name in ALLOWLIST:
            continue
        try:
            text = (ROOT / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable
        for number, line in enumerate(text.splitlines(), 1):
            if ACCENTED.search(line):
                found.append(f"{name}:{number}: {line.strip()[:80]}")
    assert not found, "accented letters found:\n" + "\n".join(found)
