
class ParameterList():

    def __init__(self):
        pass

    def add(self, parameter):
        self.check_parameter(parameter)
        setattr(self, parameter.name, parameter)
    
    def check_parameter(self, parameter):
        if hasattr(self, parameter.name):
            raise ValueError("parameter names must be unique!")
