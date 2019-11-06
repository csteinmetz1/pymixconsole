from ..processor import Processor

class Gain(Processor):
    def __init__(self, name="Gain", parameters={"gain" : 0.0}, block_size=512, sample_rate=44100):
        super().__init__(name, parameters, block_size, sample_rate)

    def process(self, data):
        return self.db2linear(self.parameters['gain']) * data
