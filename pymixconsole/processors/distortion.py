import numpy as np
from numba import jit, float64

from ..parameter import Parameter
from ..processor import Processor
from ..parameter_list import ParameterList

@jit(nopython=True)
def soft_clip(data, invert):
    if invert:
        return -1.0 * data
    else:
        return data

@jit(nopython=True)
def hard_clip(data, threshold_dB):

    M = data.shape[0]
    threshold_linear = np.power(10, threshold_dB/20)

    for n in np.arange(M):
        if data[n] > threshold_linear:
            data[n] = threshold_linear
        elif data[n] < -threshold_linear:
            data[n] = -threshold_linear

    return data

@jit(nopython=True)
def soft_clip(data, factor):
    return data - (factor * np.power(data, 3))

class Distortion(Processor):
    def __init__(self, name="Distortion", parameters=None, block_size=512, sample_rate=44100):

        super().__init__(name, parameters, block_size, sample_rate)

        if not parameters:
            self.parameters = ParameterList()
            self.parameters.add(Parameter("bypass",     False, "bool",   processor=self, p=0.1))
            self.parameters.add(Parameter("mode",      "soft", "string", processor=None, options=["soft", "hard", "infinite"]))
            self.parameters.add(Parameter("threshold",    0.0, "float",  processor=None, units="dB", maximum=0.0, minimum=-80.0))
            self.parameters.add(Parameter("factor",       0.0, "float",  processor=None, maximum=10.0, minimum=0.0))

    def process(self, data):
        if not self.parameters.bypass.value:
            if self.parameters.mode.value == "hard":
                return hard_clip(data, self.parameters.threshold.value)
            if self.parameters.mode.value == "soft":
                return soft_clip(data, self.parameters.factor.value)
        else:
            return data
