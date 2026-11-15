import random
import string
import sys

from speedupy import deterministic


def random_str(length=20):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@deterministic
def func(i: int, v: set = None, func_globals=None):
    print("stdout msg")
    print("stderr msg", file=sys.stderr)
    return 2
