from numba import jit
import numpy as np
import scipy.signal

@jit(nopython=True)
def n_process(data, buffer, buffer_size, buffer_idx, feedback):

    M = data.shape[0]

    for n in np.arange(M):

        in_sample  = data[n]
        buffer_out = buffer[buffer_idx]
        out_sample = -data[n] + buffer_out

        buffer[buffer_idx] = in_sample + (buffer_out*feedback)
        data[n] = out_sample

        buffer_idx += 1

        if buffer_idx >= buffer_size:
            buffer_idx = 0

    return data, buffer, buffer_idx

class Allpass(object):

    def __init__(self, buffer_size, feedback, block_size):
        self.block_size = block_size
        self._buffer_size = buffer_size
        self._feedback = feedback

        self.buffer = np.zeros(buffer_size)
        self.buffer_idx  = 0

    def process(self, data):
        data, self.buffer, self.buffer_idx = n_process(data, self.buffer, self.buffer_size, self.buffer_idx, self.feedback)
        return data

    def reset(self):
        self._buffer = np.zeros(buffer_size)
        self._buffer_idx  = 0

    @property
    def feedback(self):
        return self._feedback

    @feedback.setter
    def feedback(self, feedback):
        self._feedback = feedback

    @property
    def buffer_size(self):
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, buffer_size):
        self._buffer_size = buffer_size
        self.reset()
