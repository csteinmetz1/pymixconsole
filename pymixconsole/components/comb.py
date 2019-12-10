from numba import jit
import numpy as np
import scipy.signal

@jit(nopython=True)
def n_process(data, buffer, buffer_size, buffer_idx, filterstore, feedback, damp1, damp2):

    M = data.shape[0]

    for n in np.arange(M):

        in_sample = data[n]
        out_sample = buffer[buffer_idx]

        filterstore = (out_sample*damp2) + (filterstore*damp1)
        buffer[buffer_idx] = in_sample + (filterstore*feedback)
        data[n] = out_sample

        buffer_idx += 1
 
        if buffer_idx >= buffer_size:
            buffer_idx = 0

    return data, buffer, buffer_idx, filterstore

class Comb(object):

    def __init__(self, buffer_size, damp, feedback, block_size):
        self.block_size = block_size
        self.buffer_size = buffer_size
        self.feedback = feedback
        self.damp = damp

        self.reset()

    def process(self, data):
        data, self._buffer, self._buffer_idx, self._filterstore = n_process(data, self._buffer, self.buffer_size, self._buffer_idx, self._filterstore, self.feedback, 0, 0)#self._damp1, self._damp2)
        return data

    def reset(self):
        self._buffer = np.zeros(self.buffer_size)
        self._buffer_idx  = 0
        self._filterstore = 0.0

    @property
    def feedback(self):
        return self._feedback

    @feedback.setter
    def feedback(self, feedback):
        self._feedback = feedback

    @property
    def damp(self):
        return self._damp

    @damp.setter
    def damp(self, damp):
        self._damp = damp
        self._damp1 = damp
        self._damp2 = 1 - damp

    @property
    def buffer_size(self):
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, buffer_size):
        self._buffer_size = buffer_size
        self.reset()
