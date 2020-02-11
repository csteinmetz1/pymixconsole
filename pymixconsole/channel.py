import numpy as np

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
        self.pre_processors.add(Gain(name="pre-gain", block_size=bs, sample_rate=sr))  # input gain
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
        for processor in self.processors.get_all():
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

    def vectorize(self, static_order=None, include_order=True, order_encode_type="copy"):
        """ Create a vector of all processors with their parameter values.

        This will iterate all of the processors in section of the channel 
        (i.e. pre, core, and post processors) calling the vectorize method
        for each of those processors. 

        The ordering of the vectorized parameters will follow that of the order
        of the processors within the channel's `ProcessorList` objects. There is
        an exception for the core processors since these processors can have dynamic 
        ordering (when calling the `randomize()` method on the `channel`). 

        Since we may want the ordering of the processor parameters to remain constant
        when the ordering of the core processors is shuffled there is the option
        to pass a `static_order` list which contains strings of the names of all 
        of the processors in the core `ProcessorList` object.

        e.g.
        >> static_order = ["eq", "compressor"]

        Note: make sure to use the same strings as specified in the `processor.name`
        attribute for each processor object. If you omit a processor from this list
        it will not be included in the vectorized parameters. 

        The `include_order` flag will determine whether or not we append a one-hot 
        encoded vector or an integer (based upon the keyword argument flag) 
        at the end of the processors vectorized parameters which specifies its order
        in the signal processing chain. This is essentially required when the 
        `static_order` list is provided, otherwise there will be confusion about the
        correspondence between the processors and their vectorized parameters. 
        """
        vals = []

        # first vectorize the pre-processors
        for idx, processor in enumerate(self.pre_processors.get_all()):
            vec = processor.vectorize()
            #vec.append(idx)
            for v in vec:
                vals.append(v)

        # now go over the core processors (which can have dynamic ordering)
        if static_order is not None:
            if order_encode_type == "copy":
                for idx, processor in enumerate(self.processors.get_all()):
                    for processor_name in static_order:
                        vec = self.processors.get(processor_name).vectorize()
                        if processor.name != processor_name:
                            vec = np.zeros(len(vec))
                        for v in vec:
                            vals.append(v)

            elif order_encode_type == "one_hot":
                for processor_name in static_order:
                    for idx, processor in enumerate(self.processors.get_all()):
                        if processor.name == processor_name:
                            vec = processor.vectorize()
                            for v in vec:
                                vals.append(v)
        else:
            for idx, processor in enumerate(self.processors.get_all()):
                vec = processor.vectorize()
                if include_order:
                    if order_encode_type == "one_hot":
                        one_hot = np.zeros(n_proc)
                        one_hot[idx] = 1
                        for v in one_hot:
                            vec.append(v)
                    else:
                        vec.append(idx)
                for v in vec:
                    vals.append(v)
        # finally vectorize the post-processors
        for idx, processor in enumerate(self.post_processors.get_all()):
            vec = processor.vectorize()
            #vec.append(idx)
            for v in vec:
                vals.append(v)
        return vals

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