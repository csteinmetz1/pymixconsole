import numpy as np

from .processors.gain import Gain
from .processors.panner import Panner
from .processors.equaliser import Equaliser

class Channel():
    def __init__(self, sample_rate, block_size, gain):
        self.sample_rate = sample_rate
        self.block_size = block_size

        # parameters (might be better to note use a list as access is less clear)
        self.processors = [Gain(block_size=block_size, sample_rate=sample_rate),
                           Equaliser(block_size=block_size, sample_rate=sample_rate),
                           Panner(block_size=block_size, sample_rate=sample_rate)]
                           
    def process(self, ch_buffer):
        for processor in self.processors:
            ch_buffer = processor.process(ch_buffer)

        return ch_buffer