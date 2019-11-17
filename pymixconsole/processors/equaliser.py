import numpy as np

from ..processor import Processor
from ..components.irrfilter import IIRfilter

default_bands = {"low_shelf"   : {"filter_type" : "low_shelf",  "gain" : 0.0, "Fc" :    80.0, "Q" : 0.707},
                 "first_band"  : {"filter_type" : "peaking",    "gain" : 0.0, "Fc" :   200.0, "Q" : 0.707},
                 "second_band" : {"filter_type" : "peaking",    "gain" : 0.0, "Fc" :  1000.0, "Q" : 0.707},
                 "third_band"  : {"filter_type" : "peaking",    "gain" : 0.0, "Fc" :  5000.0, "Q" : 0.707},
                 "high_shelf"  : {"filter_type" : "high_shelf", "gain" : 0.0, "Fc" : 10000.0, "Q" : 0.707}}

default_params = {"in_gain" : 0.0, "out_gain" : 0.0, "bands" : default_bands}

class Equaliser(Processor):
    """ N band parametreic equaliser with customizable filter shapes

    """
    def __init__(self, name="Equaliser", parameters=default_params, block_size=512, sample_rate=44100):
        super().__init__(name, parameters, block_size, sample_rate)
        self.filters = self.setup_filters()

    def setup_filters(self):

        filters = []

        for name, band in self.parameters["bands"].items():
            filters.append(IIRfilter(band["gain"], band["Q"], band["Fc"], self.sample_rate, band['filter_type']))

        return filters

    def process(self, data):
        
        for irrfilter in self.filters:
            # apply input gain
            data *= self.db2linear(self.parameters['in_gain'])

            # apply filter
            data = irrfilter.apply_filter(data)

            # apply output gain
            data *= self.db2linear(self.parameters['out_gain'])

        return data

