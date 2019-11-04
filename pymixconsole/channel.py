import numpy as np

from .processors.gain import Gain
from .processors.panner import Panner
from .processors.equaliser import Equaliser

class Channel():
    def __init__(self, sample_rate, block_size, gain):
        self.sample_rate = sample_rate
        self.block_size = block_size

        # parameters
        self.processors = [Gain(2.0)] #Equaliser(sample_rate=self.sample_rate)

    def process(self, ch_buffer):
        for processor in self.processors:

            # this logic is janky so fix soon 
            # we need standardization, 
            # right now the panner turns the track stereo, 
            # this should happen from the stae

            if ch_buffer.ndim == 1:
                ch_buffer = processor.process(ch_buffer)

            elif ch_buffer.ndim == 2:
                for ch in np.arange(ch_buffer.ndim):
                    ch_buffer[:,ch] = processor.process(ch_buffer[:,ch])
        
        return ch_buffer