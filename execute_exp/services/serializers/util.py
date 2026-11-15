from types import FunctionType
from typing import Any, Optional, Set

import numpy as np


def to_canonical(obj: Any, visited: Optional[Set] = None) -> Any:
    if visited is None:
        visited = set()

    obj_id = id(obj)
    if obj_id in visited:
        return "<CYCLE>"

    visited.add(obj_id)

    # --- Primitive ---
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    # --- Functions (your logic, but canonical) ---
    if isinstance(obj, FunctionType):
        return {
            "__function__": obj.__name__,
            "code": obj.__code__.co_code.hex(),
            "defaults": to_canonical(obj.__defaults__, visited),
        }

    # --- NumPy ---
    if isinstance(obj, np.ndarray):
        return {
            "__ndarray__": obj.tolist(),
            "dtype": str(obj.dtype),
            "shape": obj.shape,
        }

    if isinstance(obj, np.generic):
        return obj.item()

    # --- Dict (SORTED!) ---
    if isinstance(obj, dict):
        return {
            str(k): to_canonical(v, visited)
            for k, v in sorted(obj.items(), key=lambda x: str(x[0]))
        }

    # --- List / Tuple ---
    if isinstance(obj, (list, tuple)):
        return [to_canonical(v, visited) for v in obj]

    # --- Set (CRITICAL FIX) ---
    if isinstance(obj, set):
        return sorted(to_canonical(v, visited) for v in obj)

    # --- Objects ---
    if hasattr(obj, "__dict__"):
        return {
            "__class__": obj.__class__.__name__,
            "__module__": obj.__class__.__module__,
            "attributes": {
                k: to_canonical(v, visited)
                for k, v in sorted(vars(obj).items())
                if not callable(v) and not k.startswith("_")
            },
        }

    # --- Slots ---
    if hasattr(obj, "__slots__"):
        return {
            "__class__": obj.__class__.__name__,
            "__slots__": {
                slot: to_canonical(getattr(obj, slot), visited)
                for slot in sorted(obj.__slots__)
                if hasattr(obj, slot)
            },
        }

    # --- Fallback ---
    return str(obj)
