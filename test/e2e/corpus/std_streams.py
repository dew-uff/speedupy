"""A cached function that writes to stdout and stderr: a hit must replay both."""

import sys

from speedupy.speedupy import deterministic


@deterministic
def report(name, value):
    print(f"report {name}: {value}")
    print(f"warning about {name}", file=sys.stderr)
    sys.stdout.write("no newline, ")
    return value * 2


def main():
    print("start")
    print(report("a", 1))
    print(report("b", 2))
    # The same call again: a hit within the run as well as across runs.
    print(report("a", 1))
    print("end", file=sys.stderr)


if __name__ == "__main__":
    main()
