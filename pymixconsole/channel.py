import numpy as np
from itertools import permutations

from .processor_list import ProcessorList
from .processors import *

class Channel():
    def __init__(self, sample_rate, block_size):
        self.sample_rate = sample_rate
        self.block_size = block_size

        # short-hand for init
        sr = sample_rate
        bs = block_size

        # pre-processors (order is not shuffled)
        self.pre_processors = ProcessorList(block_size=bs, sample_rate=sr)
        self.pre_processors.add(Gain(name="pre-gain", block_size=bs, sample_rate=sr))
        self.pre_processors.add(PolarityInverter(name="polarity-inverter", block_size=bs, sample_rate=sr))

        # core insert processors (order is shuffled on randomize)                           
        self.processors = ProcessorList(block_size=bs, sample_rate=sr)
        self.processors.add(Equaliser(name="eq", block_size=bs, sample_rate=sr))
        self.processors.add(Compressor(name="compressor", block_size=bs, sample_rate=sr))
        self.processors.add(ConvolutionalReverb(name="reverb", block_size=bs, sample_rate=sr))
        self.processors.add(Delay(name="delay", block_size=bs, sample_rate=sr))

        # post-processors (order is not shuffled)
        self.post_processors = ProcessorList(block_size=bs, sample_rate=sr)
        self.post_processors.add(Gain(name="post-gain", block_size=bs, sample_rate=sr)) # fader
        self.post_processors.add(Panner(name="panner", block_size=bs, sample_rate=sr))

    def process(self, ch_buffer):

        for processor in self.get_all_processors():
            ch_buffer = processor.process(ch_buffer)

        return ch_buffer

    def reset(self):
        for processor in self.get_all_processors():
            processor.reset()

    def randomize(self, shuffle=True):

        # randomize each processor configuration
        for processor in self.get_all_processors():   
            processor.randomize()

        # randomize settings of core processors only
        if shuffle:
            self.processors.shuffle()

    def serialize(self):

        serialized_processors = {"pre_processors"  : [],
                                 "core_processors" : [],
                                 "post_processors" : []}

        for idx, processor in enumerate(self.pre_processors.get_all()):
            serialized_processor = {processor.name : processor.parameters.serialize()}
            serialized_processor[processor.name]["order"] = idx
            serialized_processors["pre_processors"].append(serialized_processor)

        for idx, processor in enumerate(self.processors.get_all()):
            serialized_processor = {processor.name : processor.parameters.serialize()}
            serialized_processor[processor.name]["order"] = idx
            serialized_processors["core_processors"].append(serialized_processor)

        for idx, processor in enumerate(self.post_processors.get_all()):
            serialized_processor = {processor.name : processor.parameters.serialize()}
            serialized_processor[processor.name]["order"] = idx
            serialized_processors["post_processors"].append(serialized_processor)

        return serialized_processors

    def get_all_processors(self):
        return self.pre_processors.get_all() + self.processors.get_all() + self.post_processors.get_all()

    def params_to_file(self, output_file="ch-params.txt"):
        """ Save a text file containing the parameters and vectorized verions for each proecessor. 

        """
        with open(output_file, "w") as fp:
            for proc in self.get_all_processors():
                fp.write(f"{proc.name}: ")
                for v in proc.vectorize():
                    fp.write(f"{v:0.2f} ")
                fp.write("\n")
        
            fp.write("channel: ")
            for v in self.vectorize(static_order=["eq", "compressor", "reverb", "delay"]):
                fp.write(f"{v:0.2f} ")