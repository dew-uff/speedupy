"""A recursive pure function: run 3 is served by the top-level calls alone."""

from speedupy.speedupy import deterministic


@deterministic
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def main():
    for n in (0, 1, 10, 20):
        print(f"fib({n}) = {fib(n)}")


if __name__ == "__main__":
    main()
