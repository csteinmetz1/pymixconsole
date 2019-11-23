import numpy as np

class Processor():
    def __init__(self, name, parameters, block_size, sample_rate):
        
        self.name        = name
        self.parameters  = parameters
        self.block_size  = block_size
        self.sample_rate = sample_rate

    def update(self, parameter_name):
        pass

    def reset(self):
        for name, parameter in self.parameters.items():
            parameter.reset()

    def randomize(self, distribution="uniform"):
        for name, parameter in self.parameters:
            parameter.randomize(distribution=distribution)

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        self._parameters = parameters

    @staticmethod
    def db2linear(value):
        return np.power(10, value/20)

    @staticmethod
    def linear2db(value):
        return 20 * np.log10(value)
