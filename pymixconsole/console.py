import json
import warnings
import numpy as np

from .channel import Channel
from .bus import Bus
from .util import logger

class Console:
    """ Top level interface for the mixing console. 
    
    A mix console contains a number of channels, 
    each channel has a set of processors.  

    Calling the process function of a console will
    take the audio for each channel and pass it through
    each process method of each processor, at the end summing
    all of the the outputs into the final mixdown. 

    """

    def __init__(self, multitrack=None, block_size=512, sample_rate=44100, num_channels=1, num_busses=1, verbose=False):
        """ Create a mixing console.

        There are two options to intialize a console.

        The first method involves providing a multitrack object
        with channels of audio already loaded into the object
        along with details like the block size and sampling rate.

        The second method does not require a multitrack object 
        or any audio to be loaded, but then it does require the 
        passing of parameters like `block_size`, `sample_rate`,
        and `num_channels`. You can then pass entire console 
        channel blocks into the `process_block()` function, or
        optionally load a multitrack object later. 

        It would be cool to have in here a method that will draw a 
        diagram of the mixing console routing and the parameters of 
        each processor.

        """

        if multitrack:
            self.num_output_channels = 2
            # get properties from the multitrack
            self.multitrack   = multitrack
            self.sample_rate  = multitrack.rate
            self.num_channels = multitrack.num_channels
            self.block_size   = multitrack.block_size

        elif all([block_size, sample_rate]):
            self.sample_rate  = sample_rate
            self.block_size   = block_size
            self.num_channels = num_channels
        else:
            raise ValueError("Pass either multitrack object or provide all initialization parameters.")

        self.num_busses = num_busses
        self.log = logger.createLog(logger.LOG_NAME)
        self.verbose = verbose

        # create each channel of the mix console
        self.channels = []
        for ch_idx in range(self.num_channels):
            self.channels.append(Channel(self.sample_rate, self.block_size))

        # setup some FX busses
        self.busses = []
        sends = np.zeros(self.num_channels)
        self.busses.append(Bus(self.sample_rate, self.block_size, self.num_channels))

        # setup the master bus (which is a special kind of bus)
        self.master = Bus(self.sample_rate, self.block_size, self.num_channels + self.num_busses, master=True)

    def set_console_parameters(self):
        pass

    def process_next_block(self):
        """ Process the next block of n audio channels """

        input_buffer  = next(self.multitrack)
        output_buffer = self.process_block(input_buffer)
        downmix_buffer = self.downmix_multitrack_block(output_buffer)

        return  input_buffer, downmix_buffer

    def process_block(self, block):
        """ Apply processors on the given block of audio 
        
        The input block has dimensions [samples, in_channels]
        (all inputs are mono)

        The output buffer has dimensions [samples, out_channels]
        (all output channels are stereo)
        
        """

        master_buffer = np.zeros((block.shape[0], 2))
        bus_buffer    = np.zeros((block.shape[0], 2, self.num_busses))
        ch_buffer     = np.zeros((block.shape[0], 2, self.num_channels))

        if block.ndim == 1:
            ch_buffer = np.zeros((block.shape[0], 2, self.num_channels))
            block = np.expand_dims(block, -1)
            num_block_channels = 1
        else:
            ch_buffer = np.zeros((block.shape[0], 2, self.num_channels))	
            num_block_channels = block.shape[1]

        # apply channel processing
        for ch_idx in np.arange(num_block_channels):
            ch_buffer[:,:,ch_idx] = self.channels[ch_idx].process(block[:,ch_idx])

        # take the outputs of all channels to apply bus processing
        for bus_idx in np.arange(self.num_busses):
            bus_buffer[:,:,bus_idx] = self.busses[bus_idx].process(ch_buffer)

        # finally combine channel and bus outputs for the master bus
        master_buffer = self.master.process(np.concatenate((ch_buffer, bus_buffer), axis=2))

        return master_buffer

    def downmix_multitrack_block(self, multitrack_block):

        downmix_buffer = np.zeros([multitrack_block.shape[0], self.num_output_channels])

        for ch_idx in range(self.num_channels):
            downmix_buffer += multitrack_block[:,ch_idx,:]

        if self.verbose:
            print(f"Found {np.sum(np.where(np.abs(downmix_buffer) >= 1))} possibly clipped samples.")

        return downmix_buffer

    def reset(self):
        """ Clear all processor states """
        pass

    def randomize(self):

        for channel in self.channels:
            channel.randomize()

        for bus in self.busses:
            bus.randomize()

    def serialize(self, to_json=None):

        serialized_channels = {"channels" : []}

        for channel in self.channels:
            serialized_channels["channels"].append(channel.serialize())

        if to_json:
            with open(to_json, "w") as fp:
                json.dump(serialized_channels, fp)
                self.log.info(f"wrote serialized console paramters to file: '{to_json}'")

        return serialized_channels

    @property
    def verbose(self):
        return self._verbose
    
    @verbose.setter
    def verbose(self, verbose):
        self._verbose = verbose

        if verbose:
            self.log.setLevel("DEBUG") 
            self.log.info("verbose mode enabled")
        else:
            self.log.setLevel("ERROR") 