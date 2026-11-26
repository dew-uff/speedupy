# pickle is the cache format: the threat model is in SECURITY.md.
import pickle  # nosec B403
from typing import Any, BinaryIO, Union

from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.serializers.util import to_canonical


class PickleSerializer(Serializer):
    def dumps(self, obj: Any) -> Union[bytes, str]:
        return pickle.dumps(obj)

    def loads(self, data: Union[bytes, str]) -> Any:
        # The cache is local, trusted input: the threat model is in SECURITY.md.
        return pickle.loads(data)  # nosec B301

    def dump(self, obj: Any, file: BinaryIO) -> None:
        pickle.dump(obj, file)

    def load(self, file: BinaryIO) -> Any:
        # The cache is local, trusted input: the threat model is in SECURITY.md.
        return pickle.load(file)  # nosec B301

    def serialize_to_file(self, obj: Any, filename: str) -> None:
        with open(filename, "wb") as file:
            pickle.dump(obj, file)

    def deserialize_from_file(self, filename: str) -> Any:
        with open(filename, "rb") as file:
            # The cache is local, trusted input: the threat model is in SECURITY.md.
            return pickle.load(file)  # nosec B301

    def to_canonical(self, obj: Any) -> Any:
        return to_canonical(obj)
