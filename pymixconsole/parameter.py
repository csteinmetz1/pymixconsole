import weakref
import numpy as np

from .util import logger

kinds = ["string", "int", "float", "bool"]

class Parameter(object):
    """ Processor parameter object. """

    def __init__(self, name, value, kind, processor=None, units="", minimum=None, maximum=None, options=[], print_precision=1, randomize_value=True, **kwargs):

        self.kind = kind
        self.name = name
        if processor:
            self.processor = processor
        else:
            self.processor = processor

        if   self.kind == "string":
            if len(options) < 1:
                raise ValueError("Parameter of kind 'string' must have at least one option defined.")
            self.min = 0
            self.max = len(options)-1
            self.options = options

        elif self.kind == "int" or self.kind == "float":
            if minimum is None or maximum is None:
                raise ValueError("Parameter of kind 'int' and 'float' must have minimum and maximum values defined.")
            self.min = minimum
            self.max = maximum
            self.range = np.abs(self.min - self.max)

        self.value = value
        self.units = units
        self._default = value
        self.print_precision = print_precision
        self.randomize_value = randomize_value

        for key, val in kwargs.items():
            setattr(self, key, val)

    def __repr__(self):
        if self.kind == "int":
            return f"{self.name} {self.value:d} kind: {self.kind} range: ({self.min:d} to {self.max:d})"
        elif self.kind == "float":
            s1 = f"{self.name} {self.value:.{self.print_precision}f} {self.units} "
            s2 = f"kind: '{self.kind}' "
            s3 = f"default: {self._default:.{self.print_precision}f} {self.units} "
            s4 = f"range: ({self.min:.{self.print_precision}f} to {self.max:.{self.print_precision}f})"
            return s1 + s2 + s3 + s4
        elif self.kind == "string":
            return f"{self.name} {self.value} kind: {self.kind} options: ({self.options})"
        elif self.kind == "bool":
            return f"{self.name} {self.value} kind: {self.kind}"

    def check_value(self, value):
        # if the value is a string check its in options
        if self.kind == "string":
            if not value in self.options:
                raise ValueError(f"Invalid value {value}. Must be one of {self.options}")

        # if the value is int or float check if its in valid range
        elif self.kind in ["int", "float"]:
            if value < self.min or value > self.max:
                raise ValueError(f"Invalid value {value} for {self}")

    def reset(self):
        self.value = self._default

    def randomize(self, distribution="default"):
        """ Randomize the value of a parameter.

        By default this will select a value from a uniform distribution 
        over the range [min, max] if it is a `float`, it will use a uniform 
        distriubtion over [min, max] for an `int`, and it will 
        selection an index from the options of [0, len(options)-1] if 
        it is a `string`. 

        For many parameters a uniform distribution over [min, max] is 
        a very bad choice, and instead we may want to sample the new value
        from a normal distribution (gaussian). In this cause we can set `mu` 
        and `sigma` values for a float type parameter when we create it. 
        This will force the use of normal distriubtion. If the value 
        drawn is beyond the acceptable range it is simply capped.

        Example for randomizing a gain parameter centered at 0dB
        >>> gain.randomize(distribution="normal", mu=0.0, sigma=4.0)

        """
        if distribution == "default":
            if   self.kind == "int":
                distribution = "uniform"
            elif self.kind == "float":
                if (hasattr(self, "mu") and hasattr(self, "sigma")):
                    distribution = "normal"
                else:
                    # if mu and sigma omitted we use uniform
                    distribution = "uniform"
            elif self.kind == "string":
                distribution = "uniform"
            elif self.kind == "bool":
                distribution = "uniform"
        if   distribution == "uniform":
            if   self.kind == "int" and self.min != self.max:
                self.value = np.random.randint(self.min, high=self.max)
            elif self.kind == "float":
                self.value = (np.random.rand() * self.range) + self.min
            elif self.kind == "string":
                self.value = np.random.choice(self.options)
            elif self.kind == "bool":
                self.value = np.random.choice([True, False])
        elif distribution == "normal":
            if self.kind == "int":
                raise NotImplementedError("Can only use 'uniform' for int types not 'normal'.")
            elif self.kind == "float":
                sampled_value = np.random.normal(self.mu,self.sigma)
                # check if it exceeds the bounds and then cap it
                if sampled_value > self.max:
                    sampled_value = self.max
                elif sampled_value < self.min:
                    sampled_value = self.min
                # finally set the new value
                self.value = sampled_value
            if self.kind == "string":
                raise NotImplementedError()
            if self.kind == "bool":
                raise NotImplementedError()
        else:
            raise ValueError(f"Invalid distribtuion: {distribution}.")

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self.check_value(value)
        self._value = value

        # if there is a processor reference call its update method
        # but only if we have added all parameters first?
        if self.processor and hasattr(self.processor.parameters, self.name):
            log = logger.getLog(logger.LOG_NAME)
            if self.kind == "float":
                s = f"changing {self.processor.name} {self.name} to {value:.{self.print_precision}f} {self.units}"
            else:
                s = f"changing {self.name} to {value}."
            log.info(s)
            self.processor.update(self.name)

    def serialize(self, normalize=False, one_hot_encode=False):

        # if this is a string then we use one hot encoding
        if self.kind == "string":
            if one_hot_encode:
                val = np.zeros(len(self.options))
                index = self.options.index(self.value)
                val[index] = 1
            else:
                val = self.value
        else:
            if normalize:
                if  self.max - self.min == 0:
                    val = 0
                else:
                    val = (self.value - self.min) / (self.max - self.min)
            else:
                val = self.value
        
        return val

    @property
    def kind(self):
        return self._kind
    
    @kind.setter
    def kind(self, kind):
        if kind not in kinds:
            raise ValueError(f"Invalid kind. Must be one of {kinds}.")
        self._kind = kind

    def db2linear(self):
        return np.power(10, self.value/20)

    def linear2db(self):
        return 20 * np.log10(self.value)


