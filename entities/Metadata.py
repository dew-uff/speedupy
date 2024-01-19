from typing import Optional

class Metadata():
    def __init__(self, function_hash, args, kwargs, return_value, execution_time):
        self.__id = None
        self.__function_hash = function_hash
        self.__args = args
        self.__kwargs = kwargs
        self.__return_value = return_value
        self.__execution_time = execution_time
    
    def add_parameter(self, param_name:Optional[str], param_value) -> None:
        if param_name:
            self.__kwargs[param_name] = param_value
        else:
            self.__args.append(param_value)

    @property
    def id(self):
        return self.__id
    
    @property
    def function_hash(self):
        return self.__function_hash
    
    @property
    def args(self):
        return self.__args
    
    @property
    def kwargs(self):
        return self.__kwargs
    
    @property
    def return_value(self):
        return self.__return_value
    
    @property
    def execution_time(self):
        return self.__execution_time
    