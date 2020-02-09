import scipy.signal
import numpy as np

from ..processor import Processor
from ..parameter import Parameter
from ..parameter_list import ParameterList

from ..components.allpass import Allpass
from ..components.comb import Comb

# Tuning
muted        = 0.0
fixedgain    = 0.015
scalewet     = 3
scaledry     = 2
scaledamp    = 0.4
scaleroom    = 0.28
offsetroom   = 0.7
stereospread = 23
scalegain    = 0.2

class AlgorithmicReverb(Processor):
    def __init__(self, name="reverb", block_size=512, sample_rate=44100):
        super().__init__(name, None, block_size, sample_rate)

        self.parameters = ParameterList()
        self.parameters.add(Parameter("bypass",    False, "bool",  processor=self, p=0.1))
        self.parameters.add(Parameter("room_size",   0.5, "float", processor=self, minimum=0.05, maximum=0.85))
        self.parameters.add(Parameter("damping",     0.1, "float", processor=self, minimum=0.0,  maximum=1.0))
        self.parameters.add(Parameter("dry_mix",     0.9, "float", processor=self, minimum=0.0,  maximum=1.0))
        self.parameters.add(Parameter("wet_mix",     0.1, "float", processor=self, minimum=0.0,  maximum=1.0))
        self.parameters.add(Parameter("width",       0.7, "float", processor=self, minimum=0.0,  maximum=1.0))

        self.update(None)

    def process(self, data):

        if data.ndim >= 2:
            dataL = data[:,0]
            if data.shape[1] == 2:
                dataR = data[:,1]
            else:
                dataR = data[:,0]
        else:
            dataL = data
            dataR = data

        output = np.zeros((data.shape[0], 2))

        if self.parameters.bypass.value:
            output[:,0] = dataL
            output[:,1] = dataR

        else:   
            xL, xR = self.process_filters(dataL.copy(), dataR.copy())

            wet1_g = self.parameters.wet_mix.value * ((self.parameters.width.value/2) + 0.5)
            wet2_g = self.parameters.wet_mix.value * ((1-self.parameters.width.value)/2)
            dry_g  = self.parameters.dry_mix.value

            output[:,0] = (wet1_g * xL) + (wet2_g * xR) + (dry_g * dataL)
            output[:,1] = (wet1_g * xR) + (wet2_g * xL) + (dry_g * dataR)

        return output

    def process_filters(self, dataL, dataR):

        xL  = self.combL1.process(dataL.copy() * scalegain)
        xL += self.combL2.process(dataL.copy() * scalegain)
        xL += self.combL3.process(dataL.copy() * scalegain)
        xL += self.combL4.process(dataL.copy() * scalegain)
        xL  = self.combL5.process(dataL.copy() * scalegain)
        xL += self.combL6.process(dataL.copy() * scalegain)
        xL += self.combL7.process(dataL.copy() * scalegain)
        xL += self.combL8.process(dataL.copy() * scalegain)

        xR  = self.combR1.process(dataR.copy() * scalegain)
        xR += self.combR2.process(dataR.copy() * scalegain)
        xR += self.combR3.process(dataR.copy() * scalegain)
        xR += self.combR4.process(dataR.copy() * scalegain)
        xR  = self.combR5.process(dataR.copy() * scalegain)
        xR += self.combR6.process(dataR.copy() * scalegain)
        xR += self.combR7.process(dataR.copy() * scalegain)
        xR += self.combR8.process(dataR.copy() * scalegain)

        yL1 = self.allpassL1.process(xL)
        yL2 = self.allpassL2.process(yL1)
        yL3 = self.allpassL3.process(yL2)
        yL4 = self.allpassL4.process(yL3)

        yR1 = self.allpassR1.process(xR)
        yR2 = self.allpassR2.process(yR1)
        yR3 = self.allpassR3.process(yR2)
        yR4 = self.allpassR4.process(yR3)

        return yL4, yR4

    def update(self, parameter_name):

        rs = self.parameters.room_size.value
        dp = self.parameters.damping.value
        ss = stereospread

        # initialize allpass and feedback comb-filters
        # (with coefficients optimized for fs=44.1kHz)
        self.allpassL1 = Allpass(556,    rs, self.block_size)
        self.allpassR1 = Allpass(556+ss, rs, self.block_size)
        self.allpassL2 = Allpass(441,    rs, self.block_size)
        self.allpassR2 = Allpass(441+ss, rs, self.block_size)
        self.allpassL3 = Allpass(341,    rs, self.block_size)
        self.allpassR3 = Allpass(341+ss, rs, self.block_size)
        self.allpassL4 = Allpass(225,    rs, self.block_size)
        self.allpassR4 = Allpass(255+ss, rs, self.block_size)    

        self.combL1 = Comb(1116,    dp, rs, self.block_size)
        self.combR1 = Comb(1116+ss, dp, rs, self.block_size)
        self.combL2 = Comb(1188,    dp, rs, self.block_size)
        self.combR2 = Comb(1188+ss, dp, rs, self.block_size)
        self.combL3 = Comb(1277,    dp, rs, self.block_size)
        self.combR3 = Comb(1277+ss, dp, rs, self.block_size)
        self.combL4 = Comb(1356,    dp, rs, self.block_size)
        self.combR4 = Comb(1356+ss, dp, rs, self.block_size)
        self.combL5 = Comb(1422,    dp, rs, self.block_size)
        self.combR5 = Comb(1422+ss, dp, rs, self.block_size)
        self.combL6 = Comb(1491,    dp, rs, self.block_size)
        self.combR6 = Comb(1491+ss, dp, rs, self.block_size)
        self.combL7 = Comb(1557,    dp, rs, self.block_size)
        self.combR7 = Comb(1557+ss, dp, rs, self.block_size)
        self.combL8 = Comb(1617,    dp, rs, self.block_size)
        self.combR8 = Comb(1617+ss, dp, rs, self.block_size)
