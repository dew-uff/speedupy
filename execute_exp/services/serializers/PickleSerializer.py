import pickle
from typing import Any, Union

from execute_exp.services.serializers.Serializer import Serializer


class PickleSerializer(Serializer):
    def dumps(self, obj: Any) -> Union[bytes, str]:
        return pickle.dumps(obj)

    def loads(self, data: Union[bytes, str]) -> Any:
        return pickle.loads(data)
