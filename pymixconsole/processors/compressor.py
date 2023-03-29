from numba import jit
import numpy as np

from ..processor import Processor
from ..parameter import Parameter
from ..parameter_list import ParameterList

@jit(nopython=True)
def n_process(data, buffer, M, threshold, attack_time, release_time, ratio, makeup_gain, sample_rate, yL_prev):

    x_g = np.zeros(M)
    x_l = np.zeros(M)
    y_g = np.zeros(M)
    y_l = np.zeros(M)
    c   = np.zeros(M)

    alpha_attack  = np.exp(-1/(0.001 * sample_rate * attack_time))
    alpha_release = np.exp(-1/(0.001 * sample_rate * release_time))

    for i in np.arange(M):
        if np.abs(buffer[i]) <  0.000001:
            x_g[i] = -120.0
        else:
            x_g[i] = 20 * np.log10(np.abs(buffer[i]))

        if x_g[i] >= threshold:
            y_g[i] = threshold + (x_g[i] - threshold) / ratio
        else:
            y_g[i] = x_g[i]
            
        x_l[i] = x_g[i] - y_g[i]

        if x_l[i] > yL_prev:
            y_l[i] = alpha_attack * yL_prev + (1 - alpha_attack ) * x_l[i]
        else:
            y_l[i] = alpha_release * yL_prev + (1 - alpha_release) * x_l[i]

        c[i] = np.power(10.0, (makeup_gain - y_l[i]) / 20.0)
        yL_prev = y_l[i]

    if False:
        data[:,0] *= c
        data[:,1] *= c
    else:
        data *= c

    return data, yL_prev

class Compressor(Processor):
    """ Single band dynamic range compressor.

    """
    def __init__(self, name="Compressor", block_size=512, sample_rate=44100):
        super().__init__(name, None, block_size, sample_rate)

        self.parameters = ParameterList()
        self.parameters.add(Parameter("threshold",      0.0, "float", units="dB", processor=self, minimum=-60.0, maximum=0.0))
        self.parameters.add(Parameter("attack_time",    2.0, "float", units="ms", processor=self, minimum=0.03,  maximum=30.0))
        self.parameters.add(Parameter("release_time",  50.0, "float", units="ms", processor=self, minimum=50.0,  maximum=3000.0))
        self.parameters.add(Parameter("ratio",          2.0, "float",             processor=self, minimum=1.0,   maximum=10.0))
        self.parameters.add(Parameter("makeup_gain",    0.0, "float", units="dB", processor=self, minimum=-12.0, maximum=12.0))

        self.yL_prev = 0

    def process(self, x):

        if not self.parameters.threshold.value == 0.0:
            # if input is stereo create mono downmix buffer
            if x.ndim == 2:
                buffer = np.squeeze((x[:,0] + x[:,1])) * 0.5
            else:
                buffer = x

            x, self.yL_prev = n_process(x,
                        buffer, 
                        x.shape[0],
                        self.parameters.threshold.value, 
                        self.parameters.attack_time.value,
                        self.parameters.release_time.value,
                        self.parameters.ratio.value,
                        self.parameters.makeup_gain.value,
                        self.sample_rate,
                        self.yL_prev)

        else:
            if x.ndim < 2: # if input is mono (samples,) add stereo dim
                x = np.expand_dims(x, 1)    
        
            if x.shape[1] == 1: # if input is mono copy L to R        
                x = np.repeat(x, 2, axis=1)

        return x

    def update(self, parameter_name):
        self.yL_prev = 0
