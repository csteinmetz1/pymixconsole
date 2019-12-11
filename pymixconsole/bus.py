import numpy as np

from .parameter import Parameter
from .processor_list import ProcessorList
from .parameter_list import ParameterList

from .processors.gain import Gain
from .processors.delay import Delay
from .processors.panner import Panner
from .processors.reverb import Reverb
from .processors.equaliser import Equaliser
from .processors.converter import Converter
from .processors.compressor import Compressor

class Bus:

    def __init__(self, sample_rate, block_size, n_inputs, sends=None, master=False):
        """ Create a bus (or aux). 

        Take channels as input and apply processing to the group

        The number of elements in sends must equal `n_inputs`, 
        or the number of channels in the console if it is a normal bus. 
        For a master bus, the number of elements in sends must be equal 
        to the number of channels in the console plus the number of busses. 
        For simplicity, in a master bus we assume all sends are 1.0 (for now).

        If no sends are passed we initalize them all to zero for a normal bus
        based on the size of n_inputs. For the master bus we initalize them all 
        to ones with the size of n_inputs.
        
        """
        self.name = "sends"
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.n_inputs = n_inputs
        self.master = master

        if not sends:
            if self.master:
                self.sends = np.ones(self.n_inputs)
            else:
                self.sends = np.zeros(self.n_inputs)
        else:
            self.sends = sends

        self.processors = ProcessorList(block_size=block_size, sample_rate=sample_rate)

        # setup the mixing inputs (channel sends)
        self.parameters = ParameterList()
        for ch_idx in np.arange(n_inputs):
            self.parameters.add(Parameter(f"ch{ch_idx}-send", self.sends[ch_idx], "float", units="linear", minimum=0.0, maximum=1.0))

        if master:
            self.processors.add(Equaliser(name="master-eq"))
            self.processors.add(Compressor(name="master-compressor"))

    def process(self, block):

        # create a stereo mixdown of all channels based on send gains
        sends = [p.value for n, p in self.parameters]
        bus_buffer = np.sum(block * sends, axis=2)

        for processor in self.processors.get_all():
            bus_buffer = processor.process(bus_buffer)

        return bus_buffer

    def randomize(self, shuffle=False):

        # randomize each processor configuration
        for processor in self.processors.get_all():   
            processor.randomize()

        # randomize the sends (only for non-master bus)
        if not self.master:
            for name, send in self.parameters:
                send.randomize()

        # randomize settings of core processors only
        if shuffle:
            self.processors.shuffle()
        