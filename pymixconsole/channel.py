import numpy as np

from .processor_list import ProcessorList

from .processors.gain import Gain
from .processors.panner import Panner
from .processors.reverb import Reverb
from .processors.equaliser import Equaliser

class Channel():
    def __init__(self, sample_rate, block_size):
        self.sample_rate = sample_rate
        self.block_size = block_size

        # add the processors                           
        self.processors = ProcessorList()
        self.processors.add(Gain(name="gain", block_size=block_size, sample_rate=sample_rate))
        self.processors.add(Equaliser(name="eq", block_size=block_size, sample_rate=sample_rate))
        self.processors.add(Reverb(name="reverb", block_size=block_size, sample_rate=sample_rate))

    def process(self, ch_buffer):
        for processor in self.processors.get_all():
            ch_buffer = processor.process(ch_buffer)

        return ch_buffer