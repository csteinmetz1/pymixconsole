import numpy as np

class Processor():
    def __init__(self, name, parameters, block_size, sample_rate):
        
        self.name        = name
        self.parameters  = parameters
        self.block_size  = block_size
        self.sample_rate = sample_rate

    def reset(self):
        for name, parameter in self.parameters.items():
            parameter.reset()

    def randomize(self, distribution="uniform"):
        for name, parameter in self.parameters.items():
            parameter.randomize(distribution=distribution)

    @staticmethod
    def db2linear(value):
        return np.power(10, value/20)

    @staticmethod
    def linear2db(value):
        return 20 * np.log10(value)
