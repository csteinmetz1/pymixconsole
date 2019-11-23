from ..parameter import Parameter
from ..processor import Processor
from ..parameter_list import ParameterList

class Gain(Processor):
    def __init__(self, name="Gain", parameters=None, block_size=512, sample_rate=44100):

        super().__init__(name, parameters, block_size, sample_rate)

        if not parameters:
            self.parameters = ParameterList()
            self.parameters.add(Parameter("gain", 0.0, "float", update=self, units="dB", minimum=-80.0, maximum=12.0))

    def process(self, data):
        return self.db2linear(self.parameters.gain.value) * data
