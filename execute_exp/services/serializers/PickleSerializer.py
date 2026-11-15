import pickle
from typing import Any, Union, BinaryIO

from execute_exp.services.serializers.Serializer import Serializer
from execute_exp.services.serializers.util import to_canonical


class PickleSerializer(Serializer):
    def dumps(self, obj: Any) -> Union[bytes, str]:
        return pickle.dumps(obj)

    def loads(self, data: Union[bytes, str]) -> Any:
        return pickle.loads(data)

    def dump(self, obj: Any, file: BinaryIO) -> None:
        pickle.dump(obj, file)

    def load(self, file: BinaryIO) -> Any:
        return pickle.load(file)

    def serialize_to_file(self, obj: Any, filename: str) -> None:
        with open(filename, "wb") as file:
            pickle.dump(obj, file)

    def deserialize_from_file(self, filename: str) -> Any:
        with open(filename, "rb") as file:
            return pickle.load(file)

    def to_canonical(self, obj: Any) -> Any:
        return to_canonical(obj)
