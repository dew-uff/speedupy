import json
from execute_exp.services.serializers.Serializer import Serializer


class Hash:
    def __init__(self, serializer: Serializer):
        self._serializer = serializer

    def get_id(self, fun_source: str, fun_args=(), fun_kwargs={}) -> str:
        canonical = {
            "args": self._serializer.to_canonical(fun_args),
            "kwargs": self._serializer.to_canonical(fun_kwargs),
            "source": fun_source,
        }

        json_str = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        return self._hash(json_str.encode("utf-8"))

    def _hash(self, data: bytes) -> str:
        pass
