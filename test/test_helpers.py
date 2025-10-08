import random, string


def random_str(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))