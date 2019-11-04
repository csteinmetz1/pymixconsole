import numpy as np
from ..processor import Processor

class Panner(Processor):
    def __init__(self, pan_val):
        super().__init__("Panner", {"pan_val" : pan_val, "outputs" : 2}, sample_rate=None)

    def process(self, data):

        output_buffer = np.zeros([data.shape[0], self.parameters['outputs']])

        # this only works for two outputs (need more complicated algo for more outputs)
        output_buffer[:,0] = self.parameters['pan_val'] * data
        output_buffer[:,1] = (1 - self.parameters['pan_val']) * data

        return output_buffer
