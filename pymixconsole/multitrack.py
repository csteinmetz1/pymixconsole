import warnings
import numpy as np
import soundfile as sf

class Multitrack():
	""" Multitrack audio object 
	
	Load audio either directly as a numpy array with shape 
	[samples, channels] or provide a list of audio files to be loaded

	All channels must have the same number of samples.
	
	"""
	def __init__(self, data=None, files=None, rate=44100, block_size=512, current_index=0):
		self.data          = data
		self.files         = files
		self.block_size    = block_size
		self.current_index = current_index

		# if files are given load them
		if self.files is not None:
			self.num_channels = len(files)
			buffer, self.rate = sf.read(files[0])
			self.num_samples = buffer.shape[0]
			self.data = np.empty([self.num_samples,self.num_channels])

			for track_idx, track_file in enumerate(self.files):
				self.data[:,track_idx], rate = sf.read(track_file) # load audio (with shape (samples, channels))
		else:
			self.num_channels = self.data[1]
			self.num_samples  = self.data[0]

		# calculate number of full blocks
		self.num_blocks = int(np.floor(self.num_samples / self.block_size))

		if self.data is None and self.files is None:
			warnings.warn("No multitrack data was loaded.")

	def __iter__(self):
		return self

	def __next__(self):
		next_index = self.current_index + self.block_size

		if next_index <= self.num_samples:
			self.current_index += self.block_size
		else:
			raise StopIteration

		return self.data[self.current_index-self.block_size:self.current_index,:]

	
