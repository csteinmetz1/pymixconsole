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
            self.parameters.add(Parameter("bypass",   False,   "bool", processor=None, p=0.1))
            self.parameters.add(Parameter("type", "sm-room", "string", processor=self, options=["sm-room", "md-room", "lg-room", "hall", "plate"]))
            self.parameters.add(Parameter("decay",      1.0,  "float", processor=self, minimum=0.0, maximum=1.0))
            self.parameters.add(Parameter("dry_mix",    1.0,  "float", processor=self, minimum=0.0, maximum=1.0))
            self.parameters.add(Parameter("wet_mix",    0.0,  "float", processor=self, minimum=0.0, maximum=1.0))

        self.impulses = {}  # dict to store numpy array for each impulse response
        self.load()         # load all impulses into the dict
        self.update("type") # pre-process current impulse ready for application

    def process(self, x):

        if x.ndim < 2: # if input is mono (samples,) add stereo dim
            x = np.expand_dims(x, 1)    
        
        if x.shape[1] == 1: # if input is mono copy L to R        
            x = np.repeat(x, 2, axis=1)

        if self.parameters.bypass.value:
            return x
        else:
            #x = np.pad(x, ((0, self.block_size),(0,0))) # zero pad the input frame
            #self.X = np.roll(self.X, 1, axis=2)         # make space for the new frame
            #self.X[:,:,0] = fft(x, axis=0)              # store the result of the fft for current frame
            #Y = np.sum(self.X * self.H, axis=2)         # multiply inputs with filters
            #y = np.real(ifft(Y, axis=0))                # convert result to the time domain (only take real part)

            y = scipy.signal.oaconvolve(x, self.h, axes=0, mode='full')
            
            overlap = self.overlap[:self.block_size]

            # there will be some overlap left over we need to save
            eoverlap = self.overlap[self.block_size:]
            if eoverlap.shape[0] == 0:
                padsize = self.block_size - overlap.shape[0]
                overlap = np.pad(overlap, ((0,padsize),(0,0)))
                eoverlap = np.zeros((self.overlap.shape))
            else:
                padsize = self.overlap.shape[0] - eoverlap.shape[0]
                eoverlap = np.pad(eoverlap, ((0,padsize),(0,0)))
            
            wet = y[:self.block_size] + overlap         # add the previous overlap to the output
            dry = x[:self.block_size,:]                 # grab the dry signal
            self.overlap = y[self.block_size:,:] + eoverlap # store the overlap for the next frame

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

            h = h.astype(np.double)/(2**16)  # convert from 16 bit into to 64 bit float
            h *= 0.125                       # perform additional scaling for headroom
            self.impulses[reverb] = h        # store into dictionary

    def update(self, parameter_name):
        # this should be updated soon so we only update certain parts
        # based on which parameters change

        if parameter_name in ["type", "decay"]:
            # load proper impulse from memory
            self.h = self.impulses[self.parameters.type.value].copy()

            # fade out the impulse based on the decay setting
            fstart = int(self.parameters.decay.value * self.h.shape[0])
            fstop  = np.min((self.h.shape[0], fstart + int(0.020*self.sample_rate))) # constant 50 ms fade out
            flen   = fstop - fstart

            # if there is a fade (i.e. decay < 1.0)
            if flen > 0 and False:
                fade = np.arange(flen)/flen             # normalized set of indices
                fade = np.power(0.1, (1-fade) * 5)      # fade gain values with 100 dB of atten
                fade = np.expand_dims(fade, 1)          # add stereo dim
                fade = np.repeat(fade, 2, axis=1)       # copy gain to stereo dim
                self.h[fstart:fstop,:] *= fade          # apply fade
                self.h = self.h[:fstop]                 # throw away faded samples

            # pad the impulse to be divsibible by block size
            #pad = self.block_size - (self.h.shape[0]%self.block_size)
            #self.h = np.pad(self.h, ((0,pad),(0,0)))

            # split the impulse into blocks of size block_size
            #nfilters = self.h.shape[0]//self.block_size
            #self.h_new = np.empty((self.block_size*2, self.h.shape[1], nfilters))

            # manually construct matrix of nfilters
            #for n in np.arange(nfilters):
            #    start = n * self.block_size
            #    stop  = start + self.block_size
            #    # zero pad each chopped impulse at the end to block_size*2 
            #    self.h_new[:,:,n] = np.pad(self.h[start:stop,:], ((0, self.block_size),(0,0)))

            #self.h = self.h_new                                         # overwrite the unraveled impulse with the chopped one
            #self.H = fft(self.h, axis=0)                                # convert to freq domain filters
            #X_init = np.zeros((self.h.shape))                           # create buffer to store past outputs in freq domain

            if self.h.shape[0] > self.block_size:
                overlap_shape = self.h.shape[0] - 1
            else:
                overlap_shape = self.h.shape[0] - 1

            ovrlp_init = np.zeros((overlap_shape,self.h.shape[1]))          # create buffer for the time-domain overlap signal
            #self.X = fft(X_init, axis=0)                               # convert zero values to freq domain
            self.overlap = ovrlp_init                                   # store zero values input buffer


