import warnings
import numpy as np
from .channel import Channel

class MixConsole():
	def __init__(self, multitrack, block_size=512):

		self.multitrack = multitrack
		self.block_size = block_size

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

		multitrack_buffer = next(self.multitrack)

		for ch_idx in range(self.num_channels):
			multitrack_buffer[:,ch_idx] = self.channels[ch_idx].process(multitrack_buffer[:,ch_idx])

		return  multitrack_buffer

	def reset(self):
		""" Clear all processor states """
		pass

	