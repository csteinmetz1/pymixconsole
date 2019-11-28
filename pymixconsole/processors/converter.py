#from numba import jit, float64
import numpy as np

from ..util import logger

from ..parameter import Parameter
from ..processor import Processor
from ..parameter_list import ParameterList

class Converter(Processor):
    def __init__(self, name="Converter", parameters=None, block_size=512, sample_rate=44100):

        super().__init__(name, parameters, block_size, sample_rate)

        if not parameters:
            self.parameters = ParameterList()
            self.parameters.add(Parameter("convert_type", "mono_to_stereo", "string", processor=self, options=["mono_to_stereo", "stereo_to_mono"]))

        self.log = logger.getLog(logger.LOG_NAME)

    def process(self, data):
        if   self.parameters.convert_type.value == "mono_to_stereo":

            # check if already stereo
            if data.ndim == 2:
                self.log.warning(f"data already stereo. doing nothing...")
                return data

            output = np.empty((data.shape[0], 2))
            output[:,0] = data
            output[:,1] = data

        elif self.parameters.convert_type.value == "stereo_to_mono":

            if data.ndim == 1:
                self.log.warning(f"data already mono. doing nothing...")
                return data

            output = np.empty((data.shape[0], 1))
            output[:,0] = (data[:,0] + data[:,1]) * 0.5

        return output
