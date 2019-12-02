
class ParameterList():

    def __init__(self):
        pass

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def __repr__(self):
        for name, parameter in self:
            return parameter.__repr__()

    def add(self, parameter):
        self.check_parameter(parameter)
        setattr(self, parameter.name, parameter)
    
    def check_parameter(self, parameter):
        if hasattr(self, parameter.name):
            raise ValueError("parameter names must be unique!")

    def serialize(self, **kwargs):
        serialized_parameters = {}
        for name, parameter in self:
            serialized_parameters[parameter.name] = parameter.serialize(**kwargs)

        return serialized_parameters
