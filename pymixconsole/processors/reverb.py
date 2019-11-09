import scipy.signal
import numpy as np

from ..processor import Processor
from ..components.allpass import Allpass
from ..components.comb import Comb

default_params = {"in_gain"       : 0.0,
                  "stereo_spread" : 23, 
                  "room_size"     : 0.8,
                  "wet_dry"       : 0.1} # 1.0 all wet; 0.0 all dry

class Reverb(Processor):
    def __init__(self, name="Reverb", parameters=default_params, block_size=512, sample_rate=44100):
        super().__init__(name, parameters, block_size, sample_rate)

        roomsize = self.parameters["room_size"]
        damp = 0.5
        ss   = 23

        self.allpassL1 = Allpass(556,    roomsize, self.block_size)
        self.allpassR1 = Allpass(556+ss, roomsize, self.block_size)
        self.allpassL2 = Allpass(441,    roomsize, self.block_size)
        self.allpassR2 = Allpass(441+ss, roomsize, self.block_size)
        self.allpassL3 = Allpass(341,    roomsize, self.block_size)
        self.allpassR3 = Allpass(341+ss, roomsize, self.block_size)
        self.allpassL4 = Allpass(225,    roomsize, self.block_size)
        self.allpassR4 = Allpass(255+ss, roomsize, self.block_size)    

        self.combL1 = Comb(1116,    damp, roomsize, self.block_size)
        self.combR1 = Comb(1116+ss, damp, roomsize, self.block_size)
        self.combL2 = Comb(1188,    damp, roomsize, self.block_size)
        self.combR2 = Comb(1188+ss, damp, roomsize, self.block_size)
        self.combL3 = Comb(1277,    damp, roomsize, self.block_size)
        self.combR3 = Comb(1277+ss, damp, roomsize, self.block_size)
        self.combL4 = Comb(1356,    damp, roomsize, self.block_size)
        self.combR4 = Comb(1356+ss, damp, roomsize, self.block_size)

    def process(self, x):

        output = np.empty((len(x), 2))

        # apply input gain 
        x *= self.db2linear(self.parameters["in_gain"])

        yL1 = self.allpassL1.process(x)
        yL2 = self.allpassL2.process(yL1)
        yL3 = self.allpassL3.process(yL2)
        yL4 = self.allpassL4.process(yL3)

        yR1 = self.allpassR1.process(x)
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

        wet_g = self.parameters["wet_dry"]
        dry_g = 1 - self.parameters["wet_dry"]

        output[:,0] = (wet_g * (xL1 + xL3 - xL2 - xL4)) + (dry_g * x)
        output[:,1] = (wet_g * (xR1 + xR3 - xR2 - xR4)) + (dry_g * x)

        return output