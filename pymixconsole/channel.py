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

        # pre-processors (order is not shuffled)
        self.pre_processors = ProcessorList(block_size=block_size, sample_rate=sample_rate)
        self.pre_processors.add(Gain(name="pre-gain"))

        # core insert processors (order is shuffled on randomize)                           
        self.processors = ProcessorList(block_size=block_size, sample_rate=sample_rate)
        self.processors.add(Equaliser(name="eq"))
        #self.processors.add(Reverb(name="reverb"))

        # post-processors (order is not shuffled)
        self.post_processors = ProcessorList(block_size=block_size, sample_rate=sample_rate)
        self.post_processors.add(Gain(name="post-gain"))
        self.post_processors.add(Panner(name="panner"))

    def process(self, ch_buffer):

        for processor in self.get_all_processors():
            ch_buffer = processor.process(ch_buffer)

        return ch_buffer

    def reset(self):
        for processor in self.processors.get_all():
            processor.reset()

    def randomize(self):

        # randomize each processor configuration
        for processor in self.get_all_processors():   
            self.processor.randomize()

        # randomize settings of core processors only
        self.processors.shuffle()

    def get_all_processors(self):
        return self.pre_processors.get_all() + self.processors.get_all() + self.post_processors.get_all()
