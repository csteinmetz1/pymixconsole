import warnings
import numpy as np
from .channel import Channel

class MixConsole():
    def __init__(self, multitrack, block_size=512):

        self.multitrack = multitrack
        self.block_size = block_size
        self.num_output_channels = 2

        # get properties from the multitrack
        self.rate         = multitrack.rate
        self.num_channels = multitrack.num_channels

        # create each channel of the mix console
        self.channels = []
        for ch_idx in range(self.num_channels):
            self.channels.append(Channel(self.rate, self.block_size, 0.0))

    def set_console_parameters(self):
        pass

    def process_block(self):
        """ Process a block of n audio channels """

        input_buffer = next(self.multitrack)
        output_buffer = np.empty([input_buffer.shape[0], input_buffer.shape[1], 2])		

        for ch_idx in range(self.num_channels):
            output_buffer[:,ch_idx,:] = self.channels[ch_idx].process(input_buffer[:,ch_idx])

        downmix_buffer = self.downmix_multitrack_block(output_buffer)

        return  input_buffer, output_buffer

    def downmix_multitrack_block(self, multitrack_block):

        downmix_buffer = np.zeros([multitrack_block.shape[0], 2])

        for ch_idx in range(self.num_channels):
            downmix_buffer += multitrack_block[:,ch_idx,:]

        return downmix_buffer

    def reset(self):
        """ Clear all processor states """
        pass

    