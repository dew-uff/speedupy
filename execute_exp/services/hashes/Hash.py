import json
from typing import Any, List

from execute_exp.services.serializers.Serializer import Serializer


class Hash:
    def __init__(self, serializer: Serializer):
        self._serializer = serializer

    def get_id(self, fun_source: str, fun_args=(), fun_kwargs=None) -> str:
        if fun_kwargs is None:
            fun_kwargs = {}
        canonical = {
            "args": self._serializer.to_canonical(fun_args),
            "kwargs": self._serializer.to_canonical(fun_kwargs),
            "source": fun_source,
        }

        leaves: List[bytes] = []
        template = self._extract_leaves(canonical, leaves)
        json_str = json.dumps(template, sort_keys=True, separators=(",", ":"))
        data = json_str.encode("utf-8")
        if leaves:
            # The JSON text never holds a raw NUL (json escapes it), so the NUL
            # ends the text; each leaf's length is in the text, in order.
            data = b"\x00".join((data, b"".join(leaves)))
        return self._hash(data)

    @classmethod
    def _extract_leaves(cls, node: Any, leaves: List[bytes]) -> Any:
        """Copy of node with each bytes leaf replaced by a placeholder.

        The leaves are collected in a fixed order (lists in order, dicts by
        sorted key), so the same canonical form always yields the same stream.
        """
        if isinstance(node, bytes):
            leaves.append(node)
            return {"__bytes__": len(leaves) - 1, "length": len(node)}
        if isinstance(node, dict):
            return {
                k: cls._extract_leaves(node[k], leaves) for k in sorted(node, key=str)
            }
        if isinstance(node, (list, tuple)):
            return [cls._extract_leaves(v, leaves) for v in node]
        return node

    def _hash(self, data: bytes) -> str:
        pass
