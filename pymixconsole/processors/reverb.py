import scipy.signal
import numpy as np

from ..processor import Processor
from ..parameter import Parameter
from ..parameter_list import ParameterList

from ..components.allpass import Allpass
from ..components.comb import Comb

class Reverb(Processor):
    def __init__(self, name="Reverb", block_size=512, sample_rate=44100):
        super().__init__(name, None, block_size, sample_rate)

        self.parameters = ParameterList()
        self.parameters.add(Parameter("room_size",     0.5, "float", processor=self, minimum=0.0, maximum=1.0))
        self.parameters.add(Parameter("damping",       0.0, "float", processor=self, minimum=0.0, maximum=1.0))
        self.parameters.add(Parameter("wet_dry",       0.1, "float", processor=self, minimum=0.0, maximum=1.0))
        self.parameters.add(Parameter("stereo_spread",  23, "int",   processor=self, minimum=0,   maximum=50))

        self.update(None)

    def process(self, data):

        # we assume input data is stereo

        output = np.empty((len(data), 2))

        yL1 = self.allpassL1.process(data)
        yL2 = self.allpassL2.process(yL1)
        yL3 = self.allpassL3.process(yL2)
        yL4 = self.allpassL4.process(yL3)

        yR1 = self.allpassR1.process(data)
        yR2 = self.allpassR2.process(yR1)
        yR3 = self.allpassR3.process(yR2)
        yR4 = self.allpassR4.process(yR3)

        xL1 = self.combL1.process(yL4)
        xL2 = self.combL2.process(yL4)
        xL3 = self.combL3.process(yL4)
        xL4 = self.combL4.process(yL4)

        xR1 = self.combR1.process(yR4)
        xR2 = self.combR2.process(yR4)
        xR3 = self.combR3.process(yR4)
        xR4 = self.combR4.process(yR4)

        wet_g = self.parameters.wet_dry.value
        dry_g = 1 - self.parameters.wet_dry.value

        output[:,0] = (wet_g * (xL1 + xL3 - xL2 - xL4)) + (dry_g * data)
        output[:,1] = (wet_g * (xR1 + xR3 - xR2 - xR4)) + (dry_g * data)

        return output

    def update(self, parameter_name):

        rs = self.parameters.room_size.value
        dp = self.parameters.damping.value
        ss = self.parameters.stereo_spread.value

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