import numpy as np
from ..processor import Processor

default_params = {"pan_val" : 0.5, "outputs" : 2, "pan_law" : "-4.5dB"}

class Panner(Processor):
    """ Simple stereo panner.

    For a mono input this will produce a stereo buffer.
    For a stereo input this will produce a stereo buffer.

    Supported pan laws: ["linear", "constant_power", "-4.5dB"]

    """

    def __init__(self, name="Panner", parameters=default_params, block_size=512, sample_rate=44100):
        super().__init__(name, parameters, block_size, sample_rate) 

        # buffer to hold 
        self.__output_buffer = np.empty([self.block_size, self.parameters['outputs']])

    def __calculate_pan_coefficents(self):
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
        theta = self.parameters["pan_val"] * (np.pi/2)

        if   self.parameters["pan_law"] == "linear":
            self.__L = ((np.pi/2) - theta) * (2/np.pi)
            self.__R = theta * (2/np.pi)
        elif self.parameters["pan_law"] == "constant_power":
            self.__L = np.cos(theta)
            self.__R = np.sin(theta)
        elif self.parameters["pan_law"] == "-4.5dB":
            self.__L = np.sqrt(((np.pi/2) - theta) * (2/np.pi) * np.cos(theta))
            self.__R = np.sqrt(theta * (2/np.pi) * np.sin(theta))
        else:
            raise ValueError(f"Invalid pan_law {self.parameters['pan_val']}.")

    def process(self, data):
        """ Apply panning gains based on chosen pan law.

        Params
        -------
        data : ndarrary
            Input audio data. (samples, channels)

        Returns
        -------
        output_buffer : ndarray
            Panned input audio. (samples, channels)
        """

        # apply the channel gains
        self.__output_buffer[:,0] = self.__L * data
        self.__output_buffer[:,1] = self.__R * data

        return self.__output_buffer

    @property
    def parameters(self):
        return self.__parameters

    @parameters.setter
    def parameters(self, parameters):
        self.__parameters = parameters
        self.__calculate_pan_coefficents()

    @property
    def block_size(self):
        return self.__block__size
    
    @block_size.setter
    def block_size(self, block_size):
        self.__block__size = block_size
        self.__output_buffer = np.empty([block_size, self.parameters['outputs']])