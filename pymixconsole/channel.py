
class Channel():
	def __init__(self, rate, block_size, gain):
		self.rate = rate
		self.block_size = block_size

		# parameters
		self.gain = gain	# gain in linear

	def process(self, ch_buffer):
		return self.gain * ch_buffer