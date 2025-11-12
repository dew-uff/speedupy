from abc import ABC, abstractmethod
from typing import Any, Union, BinaryIO, Optional, Set


class Serializer(ABC):
    @abstractmethod
    def dumps(self, obj: Any) -> Union[bytes, str]: pass

    @abstractmethod
    def loads(self, data: Union[bytes, str]) -> Any: pass

    @abstractmethod
    def dump(self, obj: Any, file: BinaryIO) -> None: pass

    @abstractmethod
    def load(self, file: BinaryIO) -> Any: pass

    @abstractmethod
    def serialize_to_file(self, obj: Any, filename: str) -> None: pass

    @abstractmethod
    def deserialize_from_file(self, filename: str) -> Any: pass

    @abstractmethod
    def clean_data(self, obj: Any, visited: Optional[Set] = None) -> Any: pass
