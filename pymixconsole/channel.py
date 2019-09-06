from .processors.gain import Gain
from .processors.panner import Panner

class Channel():
    def __init__(self, rate, block_size, gain):
        self.rate = rate
        self.block_size = block_size

        # parameters
        self.processors = [Gain(1.0), Panner(0.5)]

    def process(self, ch_buffer):
        for processor in self.processors:
            ch_buffer = processor.process(ch_buffer)
        
        return ch_buffer