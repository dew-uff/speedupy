import os, sys
from typing import Any, BinaryIO

project_folder = os.path.realpath(__file__).split('test/')[0]
sys.path.append(project_folder)

from execute_exp.services.serializers.Serializer import Serializer


class RandomFakeSerializer(Serializer):
    def __init__(self):
        self._map = {}

    def dumps(self, obj: Any) -> bytes:
        data = os.urandom(16)
        self._map[data] = obj
        return data

    def loads(self, data: bytes) -> Any:
        if data is None: raise TypeError

        return self._map[data]

    def dump(self, obj: Any, file: BinaryIO) -> None:
        """Serialize and write to an already opened binary file."""
        data = self.dumps(obj)
        file.write(data)

    def load(self, file: BinaryIO) -> Any:
        """Read serialized data from an already opened binary file."""
        data = file.read()
        return self.loads(data)

    def deserialize_from_file(self, filename: str) -> Any:
        with open(filename, 'rb') as file:
            return self.load(file)

    def serialize_to_file(self, obj: Any, filename: str) -> None:
        with open(filename, 'wb') as file:
            return self.dump(obj, file)
