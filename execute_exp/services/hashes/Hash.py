from execute_exp.services.serializers.Serializer import Serializer


class Hash():
    def __init__(self, serializer: Serializer):
        self._serializer = serializer

    def get_id(self, fun_source: str, fun_args=(), fun_kwargs={}) -> str:
        data = b''
        if fun_args != ():
            fun_args = self._serializer.clean_data(fun_args)
            data += self._serializer.dumps(fun_args)
        if fun_kwargs != {}:
            fun_kwargs = self._serializer.clean_data(fun_kwargs)
            data += self._serializer.dumps(fun_kwargs)

        data = str(data) + fun_source
        data = data.encode('utf')
        return self._hash(data)

    def _hash(self, data: bytes) -> str: pass
