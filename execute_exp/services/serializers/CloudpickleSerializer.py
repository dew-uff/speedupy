import cloudpickle
from typing import Any, Union

from execute_exp.services.serializers.Serializer import Serializer


class CloudpickleSerializer(Serializer):
    def dumps(self, obj: Any) -> Union[bytes, str]:
        return cloudpickle.dumps(obj)

    def loads(self, data: Union[bytes, str]) -> Any:
        return cloudpickle.loads(data)

    def serialize_to_file(self, obj: Any, filename: str) -> None:
        with open(filename, 'wb') as file:
            return cloudpickle.dump(obj, file)

    def deserialize_from_file(self, filename: str) -> Any:
        with open(filename, 'rb') as file:
            return cloudpickle.load(file)
