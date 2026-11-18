"""Keyword arguments, defaults and a cached function calling another one."""

from speedupy.speedupy import deterministic


@deterministic
def scale(values, factor=1, offset=0):
    return [v * factor + offset for v in values]


@deterministic
def summary(values, factor=1, offset=0):
    scaled = scale(values, factor=factor, offset=offset)
    return {"total": sum(scaled), "max": max(scaled), "scaled": scaled}


def main():
    print(summary([1, 2, 3], factor=2))
    print(summary([1, 2, 3], factor=2, offset=1))
    print(summary(values=[4, 5], offset=3))
    print(summary([4, 5], 1, 3))
    print(scale([1, 2], 3))
    print(scale([1, 2], factor=3))


if __name__ == "__main__":
    main()
