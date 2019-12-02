import numpy as np

from .processor_list import ProcessorList

from .processors.gain import Gain
from .processors.delay import Delay
from .processors.panner import Panner
from .processors.reverb import Reverb
from .processors.inverter import Inverter
from .processors.equaliser import Equaliser
from .processors.converter import Converter
from .processors.compressor import Compressor

class Channel():
    def __init__(self, sample_rate, block_size):
        self.sample_rate = sample_rate
        self.block_size = block_size

        # pre-processors (order is not shuffled)
        self.pre_processors = ProcessorList(block_size=block_size, sample_rate=sample_rate)
        self.pre_processors.add(Gain(name="pre-gain"))
        self.pre_processors.add(Inverter(name="polarity-inverter"))

        # core insert processors (order is shuffled on randomize)                           
        self.processors = ProcessorList(block_size=block_size, sample_rate=sample_rate)
        self.processors.add(Equaliser(name="eq"))
        self.processors.add(Compressor(name="compressor"))
        #self.processors.add(Delay(name="delay"))
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

    def randomize(self, shuffle=False):

        # randomize each processor configuration
        for processor in self.get_all_processors():   
            processor.randomize()

        # randomize settings of core processors only
        if shuffle:
            self.processors.shuffle()

    def serialize(self, **kwargs):

        serialized_processors = {"pre_processors"  : [],
                                 "core_processors" : [],
                                 "post_processors" : []}

        for processor in self.pre_processors.get_all():
            serialized_processor = {processor.name : processor.parameters.serialize(**kwargs)}
            serialized_processors["pre_processors"].append(serialized_processor)

        for processor in self.processors.get_all():
            serialized_processor = {processor.name : processor.parameters.serialize(**kwargs)}
            serialized_processors["core_processors"].append(serialized_processor)

        for processor in self.post_processors.get_all():
            serialized_processor = {processor.name : processor.parameters.serialize(**kwargs)}
            serialized_processors["post_processors"].append(serialized_processor)

        return serialized_processors

    def get_all_processors(self):
        return self.pre_processors.get_all() + self.processors.get_all() + self.post_processors.get_all()
