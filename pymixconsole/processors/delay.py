
import numpy as np
from numba import jit, float64


from ..parameter import Parameter
from ..processor import Processor
from ..parameter_list import ParameterList

@jit(nopython=True)
def n_process(data, buffer, read_idx, write_idx, delay, feedback, dry_mix, wet_mix):

    M = buffer.shape[0]

    for ch in np.arange(data.shape[1]):
        for n in np.arange(data.shape[0]):
            in_sample = data[n, ch]
            out_sample = (dry_mix * in_sample + wet_mix * buffer[read_idx,ch])
            buffer[write_idx,ch] = in_sample + (buffer[read_idx,ch] * feedback)

            read_idx  += 1
            write_idx += 1

            if (read_idx >= M):
                read_idx = 0

            if (write_idx >= M):
                write_idx = 0

            data[n,ch] = out_sample

    return data, buffer, read_idx, write_idx

class Delay(Processor):
    def __init__(self, name="Delay", parameters=None, block_size=512, sample_rate=44100):

        super().__init__(name, parameters, block_size, sample_rate)

        if not parameters:
            self.parameters = ParameterList()
            self.parameters.add(Parameter("delay",   5000, "int",   processor=self, units="samples", minimum=0, maximum=65536))
            self.parameters.add(Parameter("feedback", 0.3, "float", processor=self, units="samples", minimum=0, maximum=1.0))
            self.parameters.add(Parameter("dry_mix",  0.9, "float", processor=self, units="samples", minimum=0, maximum=1.0))
            self.parameters.add(Parameter("wet_mix",  0.0, "float", processor=self, units="samples", minimum=0, maximum=1.0))

        self.buffer = np.zeros((65536, 2))
        self.read_idx = 0
        self.write_idx = self.parameters.delay.value

    def process(self, data):
        out, self.buffer, self.read_idx, self.write_idx = n_process(data, 
                                                           self.buffer, 
                                                           self.read_idx, 
                                                           self.write_idx,
                                                           self.parameters.delay.value,
                                                           self.parameters.feedback.value,
                                                           self.parameters.dry_mix.value,
                                                           self.parameters.wet_mix.value)
        return out
                                        