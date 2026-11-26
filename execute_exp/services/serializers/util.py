# pickle is the cache format: the threat model is in SECURITY.md.
import pickle  # nosec B403
import sys
from types import FunctionType
from typing import Any, Optional, Set

import numpy as np

_CYCLE = "<CYCLE>"


def _pandas_canonical(obj: Any) -> Any:
    """Canonical form of a pandas object, or None when obj is not one.

    pandas is optional: it is looked up only when the module is already
    imported, since no pandas object can exist before that.
    """
    pd = sys.modules.get("pandas")
    if pd is None:
        return None

    if isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return {"__class__": type(obj).__name__, "isoformat": obj.isoformat()}

    if isinstance(obj, pd.DataFrame):
        return {
            "__class__": "DataFrame",
            "columns": [to_canonical(c) for c in obj.columns],
            "dtypes": [str(t) for t in obj.dtypes],
            "content": pd.util.hash_pandas_object(obj, index=True).values.tobytes(),
        }

    if isinstance(obj, pd.Series):
        return {
            "__class__": "Series",
            "name": to_canonical(obj.name),
            "dtype": str(obj.dtype),
            "content": pd.util.hash_pandas_object(obj, index=True).values.tobytes(),
        }

    if isinstance(obj, pd.Index):
        return {
            "__class__": type(obj).__name__,
            "name": to_canonical(obj.name),
            "dtype": str(obj.dtype),
            "content": pd.util.hash_pandas_object(obj).values.tobytes(),
        }

    return None


def to_canonical(obj: Any, visited: Optional[Set] = None) -> Any:
    """Canonical form of obj: JSON-able values plus bytes leaves.

    visited holds the ids of the containers being walked (the current path),
    so only an object that contains itself is marked as a cycle.
    """
    if visited is None:
        visited = set()

    # --- Primitive ---
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj

    # --- Leaves that are not containers ---
    if isinstance(obj, np.ndarray):
        if obj.dtype.hasobject:
            return {
                "__ndarray__": to_canonical(obj.tolist(), visited),
                "dtype": str(obj.dtype),
                "shape": obj.shape,
            }
        return {
            "__ndarray__": np.ascontiguousarray(obj).tobytes(),
            # descr keeps byte order and, unlike dtype.str ("|V12"), the field
            # names of a structured dtype.
            "dtype": obj.dtype.descr,
            "shape": obj.shape,
        }

    if isinstance(obj, np.generic):
        return obj.item()

    pandas_form = _pandas_canonical(obj)
    if pandas_form is not None:
        return pandas_form

    # --- Containers: cycle detection by identity ---
    is_container = isinstance(obj, (dict, list, tuple, set)) or (
        hasattr(obj, "__dict__") or hasattr(obj, "__slots__")
    )
    if not is_container:
        # No known canonical form: the pickle, never str(obj).
        return pickle.dumps(obj, protocol=5)

    obj_id = id(obj)
    if obj_id in visited:
        return _CYCLE
    visited.add(obj_id)
    try:
        return _container_canonical(obj, visited)
    finally:
        visited.discard(obj_id)


def _container_canonical(obj: Any, visited: Set) -> Any:
    # --- Functions ---
    if isinstance(obj, FunctionType):
        return {
            "__function__": obj.__name__,
            "code": obj.__code__.co_code.hex(),
            "defaults": to_canonical(obj.__defaults__, visited),
        }

    # --- Dict (SORTED!) ---
    if isinstance(obj, dict):
        return {
            str(k): to_canonical(v, visited)
            for k, v in sorted(obj.items(), key=lambda x: str(x[0]))
        }

    # --- List / Tuple ---
    if isinstance(obj, (list, tuple)):
        return [to_canonical(v, visited) for v in obj]

    # --- Set (SORTED, whatever the element types) ---
    if isinstance(obj, set):
        return sorted((to_canonical(v, visited) for v in obj), key=repr)

    # --- Objects: private attributes are state too ---
    if hasattr(obj, "__dict__"):
        return {
            "__class__": obj.__class__.__name__,
            "__module__": obj.__class__.__module__,
            "attributes": {
                k: to_canonical(v, visited)
                for k, v in sorted(vars(obj).items())
                if not callable(v)
            },
        }

    # --- Slots ---
    return {
        "__class__": obj.__class__.__name__,
        "__slots__": {
            slot: to_canonical(getattr(obj, slot), visited)
            for slot in sorted(obj.__slots__)
            if hasattr(obj, slot)
        },
    }
