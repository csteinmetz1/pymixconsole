import numpy as np
import scipy.signal

class Comb(object):

    def __init__(self, buffer_size, damp, feedback, block_size):
        self.__buffer_size = buffer_size
        self.__feedback = feedback
        self.block_size = block_size

        self.calculate_coefficients()

    def process(self, block):

        y, self.zi = scipy.signal.lfilter(self.b, self.a, block, axis=0, zi=self.zi)

        return y

    def calculate_coefficients(self):
        self.b = np.array([1.0])
        self.a = np.concatenate(([1.0], np.zeros(self.buffer_size-1), [-self.feedback]))
        self.zi = np.zeros((max(len(self.a), len(self.b)) - 1,))

    @property
    def feedback(self):
        return self.__feedback

    @feedback.setter
    def feedback(self, feedback):
        self.__feedback = feedback
        self.calculate_coefficients()

    @property
    def buffer_size(self):
        return self.__buffer_size

    @buffer_size.setter
    def buffer_size(self, buffer_size):
        self.__buffer_size = buffer_size
        self.calculate_coefficients()