from numba import jit, float64
import numpy as np

from ..parameter import Parameter
from ..processor import Processor
from ..parameter_list import ParameterList

@jit(nopython=True)
def n_process(data, L, R):
    """ Apply panning gains based on chosen pan law.

    Params
    -------
    data : ndarrary
        Input audio data. (samples, channels)

    currently only support max of 2 channels

    Returns
    -------
    output_buffer : ndarray
        Panned input audio. (samples, channels)
    """

    if data.ndim < 2:
        # apply the channel gains
        output_buffer_L = L * data
        output_buffer_R = R * data
    else:
        # apply the channel gains
        output_buffer_L = L * data[:,0]
        output_buffer_R = R * data[:,1]

    return output_buffer_L, output_buffer_R

class Panner(Processor):
    """ Simple stereo panner.

    For a mono input this will produce a stereo buffer.
    For a stereo input this will produce a stereo buffer.

    Supported pan laws: ["linear", "constant_power", "-4.5dB"]

    """
    def __init__(self, name="Panner", block_size=512, sample_rate=44100):

        # default processor class constructor
        super().__init__(name, None, block_size, sample_rate) 

        self.parameters = ParameterList()
        self.parameters.add(Parameter("pan",    0.5, "float", processor=self, minimum=0.0, maximum=1.0))
        #self.parameters.add(Parameter("outputs",  2, "int", processor=self, minimum=2, maximum=2))
        self.parameters.add(Parameter("pan_law", "-4.5dB", "string", processor=self, options=["-4.5dB"]))

        # setup the coefficents based on default params
        self.update(None)

        # buffer to hold 
        self._output_buffer = np.empty([self.block_size, 2])

    def _calculate_pan_coefficents(self):
        """ Based on the set pan law deteremine the gain value
            to apply for the left and right channel to achieve panning effect.

            This operates on the assumption that the input channel is mono.
            The output data will be stereo at the moment, but could be expnanded
            to a higher channel count format. 

            The panning value is in the range [0, 1], where
            0 means the signal is panned completely to the left, and
            1 means the signal is apanned copletely to the right.
        """

        # first scale the linear [0, 1] to [0, pi/2]
        theta = self.parameters.pan.value * (np.pi/2)

        if   self.parameters.pan_law.value == "linear":
            self._L = ((np.pi/2) - theta) * (2/np.pi)
            self._R = theta * (2/np.pi)
        elif self.parameters.pan_law.value == "constant_power":
            self._L = np.cos(theta)
            self._R = np.sin(theta)
        elif self.parameters.pan_law.value == "-4.5dB":
            self._L = np.sqrt(((np.pi/2) - theta) * (2/np.pi) * np.cos(theta))
            self._R = np.sqrt(theta * (2/np.pi) * np.sin(theta))
        else:
            raise ValueError(f"Invalid pan_law {self.parameters.pan_law.value}.")

    def process(self, data):
        L, R = n_process(data, self._L, self._R)
        return np.stack((L, R), axis=1)

    def update(self, parameter_name):
        self._calculate_pan_coefficents()

    @property
    def block_size(self):
        return self._block_size
    
    @block_size.setter
    def block_size(self, block_size):
        self._block_size = block_size
        self._output_buffer = np.empty([block_size, 2])