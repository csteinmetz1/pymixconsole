import numpy as np
from abc import ABC, abstractmethod

class Processor(ABC):
    def __init__(self, name, parameters, block_size, sample_rate, dtype="float32"):
        
        self.name        = name
        self.parameters  = parameters
        self.block_size  = block_size
        self.sample_rate = sample_rate
        self.dtype       = dtype

        if not np.log2(block_size).is_integer():
            raise ValueError(f"Processor block size {block_size} must be a power of 2.")

    @abstractmethod
    def process(self):
        pass
        
    @abstractmethod
    def update(self, parameter_name):
        pass

    def set(self, config):
        for parameter_name, settings in config.items():
            parameter = getattr(self.parameters, parameter_name)
            for setting_name, value in settings.items():
                setattr(parameter, setting_name, value)

    def reset(self):
        for name, parameter in self.parameters:
            parameter.reset()

    def randomize(self, **kwargs):
        for name, parameter in self.parameters:
            if parameter.randomize_value:
                parameter.hold = True # hold updates til end
                parameter.randomize()
        self.update(None)

    def serialize(self):
        """ Create dict with details on all parameter values.

        This will create a dictionary with each parameter value along with
        its minimum and maximum value (if float or int), the options (if string),
        or simply its value if its a boolean value. 

        """
        return self.parameters.serialize()

    def vectorize(self, **kwargs):
        """ Create a list with normalized parameter values.

        This method will seralize all the parameters and then use the
        approproaite method to normalize all values between 0 and 1, 
        or perform one hot encoding for string values. 

        Parameters always appear in the same order, based on when
        they were created and added to the processors's ParameterList.

        """
        vals = []
        for name, param in self.serialize().items():
            # check if there is a min and max (float or int)
            if ("min" in param) and ("max" in param):
                if param["max"] - param["min"] == 0:
                    val = 0
                else:
                    val = (param["value"] - param["min"]) / (param["max"] - param["min"])
                    val = (val * 2) - 1
            # check if there are options (string)
            elif "options" in param:
                n_options = len(param["options"])
                val = np.zeros(n_options)
                index = param["options"].index(param["value"])
                val[index] = 1
                val = list(val)
            # otherwise its a boolean case
            else:
                val = param["value"] / 1

            # if we have one-hot-encoded vector append elements one by one
            if isinstance(val, list):
                for v in val:
                    vals.append(v)
            else:
                vals.append(val)
        return vals

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        self._parameters = parameters

    @staticmethod
    def db2linear(value):
        return np.power(10, value/20)

    @staticmethod
    def linear2db(value):
        return 20 * np.log10(value)
