class CacheData():
    def __init__(self, function_call_hash:str, output, func_name=None, id=None):
        self.__id = id
        self.__function_call_hash = function_call_hash
        self.__output = output
        self.__func_name = func_name

    @property
    def id(self):
        return self.__id

    @property
    def function_call_hash(self):
        return self.__function_call_hash

    @property
    def output(self):
        return self.__output

    @property
    def func_name(self):
        return self.__func_name
