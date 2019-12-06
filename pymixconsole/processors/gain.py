from numba import jit, float64

from ..parameter import Parameter
from ..processor import Processor
from ..parameter_list import ParameterList

@jit(nopython=True)
def n_process(data, gain):
    return gain * data

class Gain(Processor):
    def __init__(self, name="Gain", parameters=None, block_size=512, sample_rate=44100):

        super().__init__(name, parameters, block_size, sample_rate)

        if not parameters:
            self.parameters = ParameterList()
            self.parameters.add(Parameter("bypass", False, "bool", processor=None))
            self.parameters.add(Parameter("gain", 0.0, "float", processor=None, units="dB", minimum=-80.0, maximum=24.0, mu=0.0, sigma=4.0))

    def process(self, data):
        if self.parameters.bypass.value:
            return data
        else:
            return n_process(data, self.db2linear(self.parameters.gain.value))
