import pickle
from typing import Any, Union

from execute_exp.services.serializers.Serializer import Serializer


class PickleSerializer(Serializer):
    def dumps(self, obj: Any) -> Union[bytes, str]:
        return pickle.dumps(obj)

    def loads(self, data: Union[bytes, str]) -> Any:
        return pickle.loads(data)

    def serialize_to_file(self, obj: Any, filename: str) -> None:
        with open(filename, 'wb') as file:
            return pickle.dump(obj, file)

    def deserialize_from_file(self, filename: str) -> Any:
        with open(filename, 'rb') as file:
            return pickle.load(file)
