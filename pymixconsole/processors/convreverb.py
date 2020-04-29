FFT_TYPE = "scipy"

import os
import pathlib
import warnings
import numpy as np
import scipy.signal
from scipy.io import wavfile

from ..parameter import Parameter
from ..processor import Processor
from ..parameter_list import ParameterList

if FFT_TYPE == "scipy": 
    from scipy.fftpack import fft, ifft
else:                   
    from numpy.fft import fft, ifft

# Impulse responses
ir_dir = "irs"
src = {"sm-room" : "small_room.wav",
       "md-room" : "medium_room.wav",
       "lg-room" : "large_room.wav",
       "hall"    : "hall.wav",
       "plate"   : "plate.wav"}

class ConvolutionalReverb(Processor):
    def __init__(self, name="reverb", parameters=None, block_size=512, sample_rate=44100):

        super().__init__(name, parameters, block_size, sample_rate)

        if not parameters:
            self.parameters = ParameterList()
            self.parameters.add(Parameter("type", "sm-room", "string", processor=self, options=["sm-room", "md-room", "lg-room", "hall", "plate"]))
            self.parameters.add(Parameter("decay",      1.0,  "float", processor=self, minimum=0.1, maximum=1.0))
            self.parameters.add(Parameter("dry_mix",    1.0,  "float", processor=self, minimum=0.0, maximum=1.0))
            self.parameters.add(Parameter("wet_mix",    0.0,  "float", processor=self, minimum=0.0, maximum=1.0))

        self.impulses = {}  # dict to store numpy array for each impulse response
        self.load()         # load all impulses into the dict
        self.update("type") # pre-process current impulse ready for application

    def process(self, x):

        if x.ndim < 2: # if input is mono (samples,) add stereo dim
            x = np.expand_dims(x, 1)    
        
        if x.shape[1] == 1: # if input is mono copy L to R       
            mono = True 
            x = np.repeat(x, 2, axis=1)

        if self.parameters.wet_mix.value == 0.0:
            return x
        else:
            # perform partitioned convolution
            y = scipy.signal.fftconvolve(x, self.h, axes=0, mode='full')

            # pick out the previous overlap that will be added to output
            overlap = self.overlap[:self.block_size]

            # there may be some overlap left over we need to save again
            eoverlap = self.overlap[self.block_size:]
            if eoverlap.shape[0] == 0:
                padsize = self.block_size - overlap.shape[0]
                overlap = np.pad(overlap, ((0,padsize),(0,0)))
                eoverlap = np.zeros((self.overlap.shape))
            else:
                padsize = self.overlap.shape[0] - eoverlap.shape[0]
                eoverlap = np.pad(eoverlap, ((0,padsize),(0,0)))
            
            wet = y[:self.block_size] + overlap             # add the previous overlap to the output
            dry = x[:self.block_size,:]                     # grab the dry signal
            self.overlap = y[self.block_size:,:] + eoverlap # store the overlap for the next frame (with extra overlap)

            wet *= self.parameters.wet_mix.value        # apply gain to wet signal
            dry *= self.parameters.dry_mix.value        # apply gain to input (dry) signal
            out = wet + dry                             # mix wet and dry signals

            return out

    def load(self):

        # read all impulse responses from disk and store
        for reverb in self.parameters.type.options:
            curdir = pathlib.Path(__file__).parent.absolute()
            filename = os.path.join(curdir, "..", ir_dir, src[reverb])

            sr, h = wavfile.read(filename)   # load the audio file for correct impulse response

            # check if the sample rate matches processor
            if sr != self.sample_rate:
                # for now we raise an error. but in the future we would want to automatically resample
                raise RuntimeError(f"Sample rate of impulse {sr} must match sample rate of processor {self.sample_rate}")

            h = h/32767                      # convert from 16 bit into to 32 bit float
            h *= 0.125                       # perform additional scaling for headroom
            self.impulses[reverb] = h.astype(self.dtype)        # store into dictionary

    def update(self, parameter_name=None):
        # this should be updated soon so we only update certain parts
        # based on which parameters change

        # load proper impulse from memory
        self.h = self.impulses[self.parameters.type.value].copy()

        # fade out the impulse based on the decay setting
        fstart = int(self.parameters.decay.value * self.h.shape[0])
        fstop  = np.min((self.h.shape[0], fstart + int(0.020*self.sample_rate))) # constant 50 ms fade out
        flen   = fstop - fstart

        # if there is a fade (i.e. decay < 1.0)
        if flen > 0 and True:
            fade = np.arange(flen, dtype=self.dtype)/flen # normalized set of indices
            fade = np.power(0.1, (1-fade) * 5)            # fade gain values with 100 dB of atten
            fade = np.expand_dims(fade, 1)                # add stereo dim
            fade = np.repeat(fade, 2, axis=1)             # copy gain to stereo dim
            self.h[fstart:fstop,:] *= fade                # apply fade
            self.h = self.h[:fstop]                       # throw away faded samples

        self.reset_state() # set the internal buffer to zeros

    def reset_state(self):
        overlap_shape = self.h.shape[0] - 1                         # overlap buffer size 
        overlap_init = np.zeros((overlap_shape,self.h.shape[1]))    # create buffer for the time-domain overlap signal
        self.overlap = overlap_init.astype(self.dtype)              # store zero values input buffer
        