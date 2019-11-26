import weakref
import numpy as np

from .util import logger

class Parameter(object):

    def __init__(self, name, value, kind, processor=None, units="", minimum=None, maximum=None, options=[], print_precision=1):

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

    def __repr__(self):
        if self.kind == "int":
            return f"{self.name} {self.value:d} kind: {self.kind} ({self.min:d} to {self.max:d})"
        elif self.kind == "float":
            return f"{self.name} {self.value:.{self.print_precision}f} {self.units} kind: '{self.kind}' default: {self._default:.{self.print_precision}f} {self.units} range: ({self.min:.{self.print_precision}f} to {self.max:.{self.print_precision}f})"
        elif self.kind == "string":
            return f"{self.name} {self.value} kind: {self.kind} options: ({self.options})"

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

    def randomize(self, distribution="uniform", p=[]):
        if   distribution == "uniform":
            if   self.kind == "int" and self.min != self.max:
                self.value = np.random.randint(self.min, high=self.max)
            elif self.kind == "float":
                self.value = (np.random.rand() * self.range) + self.min
            elif self.kind == "string":
                self.value = np.random.choice(self.options)
        elif distribution == "normal":
            if self.kind == "int":
                raise NotImplementedError()
            elif self.kind == "float":
                mu = self.range/2
                sigma = (mu/3)
                # this may not make a lot of sense
                self.value = np.random.normal(mu, sigma) - np.abs(self.min)
            if self.kind == "string":
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
            log = logger.getLog("console")
            log.info(f"changing {self.name} to {value}.")
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
                val = self.value / self.max
            else:
                val = self.value
        
        return val

    @property
    def kind(self):
        return self._kind
    
    @kind.setter
    def kind(self, kind):
        if kind not in ["string", "int", "float"]:
            raise ValueError("Invalid kind. Must be 'string', 'int', or 'float'.")
        self._kind = kind

    def db2linear(self):
        return np.power(10, self.value/20)

    def linear2db(self):
        return 20 * np.log10(self.value)


