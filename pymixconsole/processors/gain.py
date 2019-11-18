from ..parameter import Parameter
from ..processor import Processor

default_parameters = {"gain_val" : Parameter(0.0, "float", units="dB", minimum=-80.0, maximum=12.0)}

class Gain(Processor):
    def __init__(self, name="Gain", parameters=default_parameters, block_size=512, sample_rate=44100):
        super().__init__(name, parameters, block_size, sample_rate)

    def process(self, data):
        return self.db2linear(self.parameters["gain_val"]) * data
