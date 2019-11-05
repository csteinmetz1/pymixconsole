import warnings
import numpy as np
from .channel import Channel

class MixConsole():
    def __init__(self, multitrack, block_size=512, verbose=False):

        self.multitrack = multitrack
        self.block_size = block_size
        self.num_output_channels = 2
        self.verbose = verbose

        # get properties from the multitrack
        self.sample_rate  = multitrack.rate
        self.num_channels = multitrack.num_channels

        # create each channel of the mix console
        self.channels = []
        for ch_idx in range(self.num_channels):
            self.channels.append(Channel(self.sample_rate, self.block_size, 0.0))

    def set_console_parameters(self):
        pass

    def process_block(self):
        """ Process a block of n audio channels """

        input_buffer = next(self.multitrack)
        output_buffer = np.empty([input_buffer.shape[0], input_buffer.shape[1], self.num_output_channels])		

        for ch_idx, channel in enumerate(self.channels):
            output_buffer[:,ch_idx,:] = channel.process(input_buffer[:,ch_idx])

        downmix_buffer = self.downmix_multitrack_block(output_buffer)

        return  input_buffer, downmix_buffer

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

    