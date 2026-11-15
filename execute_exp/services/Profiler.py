from execute_exp.services.DataAccess import DataAccess
from SingletonMeta import SingletonMeta


class Profiler(metaclass=SingletonMeta):
    def __init__(self):
        self.num_deterministic_calls = 0
        self.num_cache_hit = 0
        self.num_func_call_too_fast_to_memoize = 0

    def report(self):
        print("----------------------- Profiler -----------------------")
        print(f"Number of calls to @deterministic: {self.num_deterministic_calls}")
        print(f"Number of cache hits: {self.num_cache_hit}")
        print(
            f"Percentage of cache hits (%): {100 * self.num_cache_hit / self.num_deterministic_calls}"
        )
        print(
            f"Number of function calls too fast to memoize: {self.num_func_call_too_fast_to_memoize}"
        )
        print(
            f"Percentage of function calls too fast to memoize (%): {100 * self.num_func_call_too_fast_to_memoize / self.num_deterministic_calls}"
        )
        print(
            f"Size of nem cache entries (MB): {DataAccess().get_new_cache_entries_size() / (1024 * 1024)}"
        )
        print("--------------------------------------------------------")
