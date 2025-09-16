import cloudpickle
from typing import Any, Union

from execute_exp.services.serializers.Serializer import Serializer


class CloudpickleSerializer(Serializer):
    def dumps(self, obj: Any) -> Union[bytes, str]:
        return cloudpickle.dumps(obj)

    def loads(self, data: Union[bytes, str]) -> Any:
        return cloudpickle.loads(data)
