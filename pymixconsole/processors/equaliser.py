import numpy as np

from ..processor import Processor
from ..parameter import Parameter
from ..parameter_list import ParameterList
from ..components.irrfilter import IIRfilter

MIN_GAIN = -12.0
MAX_GAIN =  12.0
MIN_Q    =   0.1
MAX_Q    =  10.0

class Equaliser(Processor):
    """ Five band parametreic equaliser ( two shelves and three central bands )

    All gains are set in dB values and range from -32.0 dB to +12.0 dB.
    This processor is implemented as cascade of five biquad IIR filters
    that are implemented using the infamous cookbook formulae from RBJ.

    """
    def __init__(self, name="Equaliser", block_size=512, sample_rate=44100):
        super().__init__(name, None, block_size, sample_rate)

        self.parameters = ParameterList()
        # low shelf parameters ----------------------------------------------------------------------------------------------
        self.parameters.add(Parameter("low_shelf_gain",      0.0, "float", processor=self, minimum=MIN_GAIN, maximum=MAX_GAIN))
        self.parameters.add(Parameter("low_shelf_freq",     80.0, "float", processor=self, minimum=20.0,     maximum=1000.0))
        # first band parameters ---------------------------------------------------------------------------------------------
        self.parameters.add(Parameter("first_band_gain",     0.0, "float", processor=self, minimum=MIN_GAIN, maximum=MAX_GAIN))
        self.parameters.add(Parameter("first_band_freq",   400.0, "float", processor=self, minimum=200.0,    maximum=5000.0))        
        self.parameters.add(Parameter("first_band_q",        0.7, "float", processor=self, minimum=MIN_Q,    maximum=MAX_Q))
        # second band parameters --------------------------------------------------------------------------------------------
        self.parameters.add(Parameter("second_band_gain",    0.0, "float", processor=self, minimum=MIN_GAIN, maximum=MAX_GAIN))
        self.parameters.add(Parameter("second_band_freq", 1000.0, "float", processor=self, minimum=500.0,    maximum=6000.0))        
        self.parameters.add(Parameter("second_band_q",       0.7, "float", processor=self, minimum=MIN_Q,    maximum=MAX_Q))
        # second band parameters --------------------------------------------------------------------------------------------
        self.parameters.add(Parameter("third_band_gain",     0.0, "float", processor=self, minimum=MIN_GAIN, maximum=MAX_GAIN))
        self.parameters.add(Parameter("third_band_freq",  5000.0, "float", processor=self, minimum=1000.0,    maximum=10000.0))        
        self.parameters.add(Parameter("third_band_q",        0.7, "float", processor=self, minimum=MIN_Q,    maximum=MAX_Q))
        # high shelf parameters --------------------------------------------------------------------------------------------
        self.parameters.add(Parameter("high_shelf_gain",      0.0, "float", processor=self, minimum=MIN_GAIN, maximum=MAX_GAIN))
        self.parameters.add(Parameter("high_shelf_freq",  10000.0, "float", processor=self, minimum=20.0,     maximum=20000.0))

        self.bands, self.filters = self.setup_filters()

    def setup_filters(self):

        filters = {}
        bands = ["low_shelf", "first_band", "second_band", "third_band", "high_shelf"]

        for band in bands:

            G = getattr(self.parameters, band + "_gain").value
            fc = getattr(self.parameters, band + "_freq").value
            rate = self.sample_rate

            if band in ["low_shelf", "high_shelf"]:
                Q = 0.707
                filter_type = band
            else:
                Q = getattr(self.parameters, band + "_q").value
                filter_type = "peaking"

            filters[band] = IIRfilter(G, Q, fc, rate, filter_type, n_channels=2)

        return bands, filters

    def update_filter(self, band):

        self.filters[band].G    = getattr(self.parameters, band + "_gain").value
        self.filters[band].fc   = getattr(self.parameters, band + "_freq").value
        self.filters[band].rate = self.sample_rate 

        if band in ["first_band", "second_band", "third_band"]:
            self.filters[band].Q    = getattr(self.parameters, band + "_q").value

    def update(self, parameter_name):

        band = '_'.join(parameter_name.split('_')[:2])
        self.update_filter(band)

    def process(self, data):
        
        for band, irrfilter in self.filters.items():
            data = irrfilter.apply_filter(data)

        return data

