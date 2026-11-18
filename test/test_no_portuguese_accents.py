"""Guards for Tasks 18 and 19: no accented letters and no old Portuguese names."""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Latin-1 and Latin Extended-A letters with diacritics (built from code points,
# since ruff rewrites escapes into literals and this file must stay ASCII). Typographic punctuation such as dashes, arrows and
# curly quotes is legitimate and not matched.
ACCENTED = re.compile(
    "[%s-%s%s-%s%s-%s]" % tuple(chr(c) for c in (0xC0, 0xD6, 0xD8, 0xF6, 0xF8, 0x17F))
)

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


# Guard for Task 19: the Portuguese names that were renamed must not come back.
# Each is written in two pieces so that this file does not match itself.
OLD_NAMES = re.compile(
    r"\b(?:"
    + "|".join(
        a + b
        for a, b in [
            ("Ban", r"co(?:SQLite|MySQL|Mongo|GridFS|Redis|Memcached)?"),
            ("Constan", "tes"),
            ("constan", "tes"),
            ("BD_", "PATH"),
            ("cone", "xao"),
            ("nome_", "ban" + "co"),
            ("nome_", "script"),
            ("di", "cio"),
            ("ban", "co"),
            ("li", "sta"),
            ("conjun", "to"),
            ("resul", "tado"),
        ]
    )
    + r")\b"
)

# Files that talk about the old names on purpose: the plan that lists them.
OLD_NAMES_ALLOWLIST = {"RETROFIT.md", "uv.lock"}


def test_no_old_portuguese_names_in_tracked_files():
    try:
        files = _tracked_files()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("not a git checkout")
    found = []
    for name in files:
        if name in OLD_NAMES_ALLOWLIST or not (ROOT / name).exists():
            continue
        if OLD_NAMES.search(name):
            found.append(f"{name}: file name")
        try:
            text = (ROOT / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if OLD_NAMES.search(line):
                found.append(f"{name}:{number}: {line.strip()[:80]}")
    assert not found, "old Portuguese names found:\n" + "\n".join(found)
