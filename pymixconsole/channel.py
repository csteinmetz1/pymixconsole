import numpy as np

from .processors.gain import Gain
from .processors.panner import Panner
from .processors.equaliser import Equaliser

class Channel():
    def __init__(self, sample_rate, block_size, gain):
        self.sample_rate = sample_rate
        self.block_size = block_size

        # parameters
        self.processors = [Gain(2.0), Panner(0.5), Equaliser(sample_rate=self.sample_rate)]

    def process(self, ch_buffer):
        for processor in self.processors:
            ch_buffer = processor.process(ch_buffer)

        return ch_buffer