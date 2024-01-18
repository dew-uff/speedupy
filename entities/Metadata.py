from typing import Optional

class Metadata():
    def __init__(self, id, function_hash, return_value, execution_time):
        self.__id = id
        self.__function_hash = function_hash
        self.__args = []
        self.__kwargs = {}
        self.__return_value = return_value
        self.__execution_time = execution_time
    
    def add_parameter(self, param_name:Optional[str], param_value) -> None:
        if param_name:
            self.__kwargs[param_name] = param_value
        else:
            self.__args.append(param_value)

    # @property
    # def args(self):
    #     return self.__args
    
    # @property
    # def kwargs(self):
    #     return self.__kwargs