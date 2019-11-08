import numpy as np

class Processor():
    def __init__(self, name, parameters, block_size, sample_rate):
        
        self.name        = name
        self.parameters  = parameters
        self.block_size  = block_size
        self.sample_rate = sample_rate

    @staticmethod
    def db2linear(value):
        return np.power(10, value/20)

    @staticmethod
    def linear2db(value):
        return 20 * np.log10(value)
