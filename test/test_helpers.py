import sys, random, string
from speedupy import deterministic


def random_str(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@deterministic
def func(i: int, v: set = {}, func_globals={}):
    print("stdout msg")
    print("stderr msg", file=sys.stderr)
    return 2
