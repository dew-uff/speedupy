from enum import Enum

class FunctionClassification(Enum):
    CACHE = 1
    DONT_CACHE = 2
    MAYBE_CACHE = 3
