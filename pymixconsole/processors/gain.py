from ..processor import Processor

class Gain(Processor):
    def __init__(self, gain_val):
        super().__init__("Input Gain", {"gain" : gain_val})

    def process(self, data):
        return self.parameters['gain'] * data


