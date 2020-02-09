import numpy as np

from ..parameter import Parameter
from ..processor import Processor
from ..parameter_list import ParameterList

class ConvolutionalReverb(Processor):
    def __init__(self, ir, name="reverb", parameters=None, block_size=512, sample_rate=44100):

        super().__init__(name, parameters, block_size, sample_rate)

        if not parameters:
            self.parameters = ParameterList()
            self.parameters.add(Parameter("bypass", False, "bool", processor=None))
            self.parameters.add(Parameter("gain", 0.0, "float", processor=None, units="dB", minimum=-80.0, maximum=24.0, mu=0.0, sigma=4.0))

        self.h = ir

        # for now we turn this into mono
        self.h = self.h[:,0]

        # normalize the ir
        #self.h /= np.max(self.h)
    
        # pad the input to be divsibible by block size
        pad = self.block_size - (self.h.shape[0]%self.block_size)
        self.h = np.pad(self.h, (0,pad))

        # split impulse response into frames the size of the block size
        #self.h = self.h.reshape((self.block_size,-1))

        # pad each filter to 1024 samples
        #self.h = np.pad(self.h, ((0, self.block_size), (0, 0)))

        nfilters = self.h.shape[0]//self.block_size
        self.h_new = np.empty((self.block_size*2, nfilters))

        # manually construct matrix of h filters
        for n in np.arange(nfilters):
            start = n * self.block_size
            stop  = start + self.block_size
            self.h_new[:,n] = np.pad(self.h[start:stop], (0, self.block_size))

        print(self.h_new.shape)
        self.h = self.h_new

        # convert to freq domain filters
        self.H = np.fft.fft(self.h, axis=0)
        print(self.H.shape)
        
        # buffer to store past outputs in freq domain
        self.X = np.fft.fft(np.zeros((self.block_size*2, self.H.shape[1])), axis=0)

        self.overlap = np.zeros(self.block_size)

    def process(self, data):
        if self.parameters.bypass.value:
            return data
        else:

            # make space for the new frame
            self.X = np.roll(self.X, 1, axis=1)

            # zero pad the input frame
            x = np.pad(data, ((0, self.block_size)))

            # load the result of the fft for current frame
            self.X[:,0] = np.fft.fft(x, axis=0)

            # multiply outputs with filters
            Y = np.sum(self.X * self.H, axis=1)

            # convert result to the time domain
            y = np.fft.ifft(Y)

            # add the previous overlap to the output
            output = y[:self.block_size] + self.overlap

            # store the overlap
            self.overlap = y[self.block_size:]

            return output

