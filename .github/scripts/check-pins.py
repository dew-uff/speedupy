"""Fail when requirements.txt and [project.dependencies] differ.

Standard library only, so it runs on any supported Python.
Usage: python .github/scripts/check-pins.py [requirements.txt] [pyproject.toml]
"""

import re
import sys


def normalize(line):
    name, _, version = line.partition("==")
    return name.strip().lower().replace("_", "-"), version.strip()


def read_requirements(path):
    with open(path) as f:
        lines = [x.strip() for x in f if x.strip() and not x.lstrip().startswith("#")]
    return dict(normalize(x) for x in lines)


def read_pyproject(path):
    with open(path) as f:
        text = f.read()
    block = re.search(r"^dependencies\s*=\s*\[(.*?)^\]", text, re.S | re.M)
    if block is None:
        sys.exit(f"{path}: no [project] dependencies array found")
    return dict(normalize(x) for x in re.findall(r'"([^"]+)"', block.group(1)))


def main():
    req_path = sys.argv[1] if len(sys.argv) > 1 else "requirements.txt"
    pyp_path = sys.argv[2] if len(sys.argv) > 2 else "pyproject.toml"
    req, pyp = read_requirements(req_path), read_pyproject(pyp_path)
    problems = []
    for name in sorted(req.keys() | pyp.keys()):
        if name not in pyp:
            problems.append(f"{name}: only in {req_path}")
        elif name not in req:
            problems.append(f"{name}: only in {pyp_path}")
        elif req[name] != pyp[name]:
            problems.append(f"{name}: {req_path} {req[name]} != {pyp_path} {pyp[name]}")
    if problems:
        sys.exit("pins differ:\n  " + "\n  ".join(problems))
    print(f"ok: {len(req)} pins agree")


if __name__ == "__main__":
    main()
