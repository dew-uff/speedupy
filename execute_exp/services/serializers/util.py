from types import FunctionType
from typing import Any, Optional, Set
import numpy as np


def clean_data(obj: Any, visited: Optional[Set] = None) -> Any:
    """
    Recursively walk a Python object and clean its attributes so the serializer will always produce the same bytecode for the given object.
    """
    if visited is None: visited = set()

    obj_id = id(obj)
    if obj_id in visited: return obj

    visited.add(obj_id)

    if isinstance(obj, FunctionType):
        g = obj.__globals__
        if "__file__" in g:
            # Clone the globals dict so we don’t mutate shared modules
            new_globals = dict(g)
            new_globals["__file__"] = None
            obj = FunctionType(obj.__code__,
                               new_globals,
                               name=obj.__name__,
                               argdefs=obj.__defaults__,
                               closure=obj.__closure__)
        return obj

    if isinstance(obj, np.ndarray): return obj.tolist()

    if isinstance(obj, np.generic): return obj.item()

    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            obj[k] = clean_data(v, visited)
        return obj

    if isinstance(obj, (list, tuple, set)):
        container_type = type(obj)
        return container_type(clean_data(v, visited) for v in obj)

    # User-defined object
    if hasattr(obj, "__dict__"):
        for k, v in vars(obj).items():
            setattr(obj, k, clean_data(v, visited))
        return obj

    # Slots
    if hasattr(obj, "__slots__"):
        for slot in obj.__slots__:
            if hasattr(obj, slot):
                val = getattr(obj, slot)
                setattr(obj, slot, clean_data(val, visited))
        return obj

    return obj
