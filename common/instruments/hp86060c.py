from .instrument_driver_base import InstrumentDriverBase


class hp86060c(InstrumentDriverBase):
    def __init__(self, *instr):
        self.instr = instr[0]

    def _set_switch(self):
        self.instr.write(':ROUTE:LAYER:CHANNEL A1,B2')

    optical = property(_set_switch, "switch")

    def _changing_switch(self):
        self.instr.write(':ROUTE:LAYER:CHANNEL A1,B3')

    spectrum_switch = property(_changing_switch, "switch for optical spectrum analyzer")

    def _changing_off(self):
        self.instr.write(':ROUTE:LAYER:CHANNEL A1,B0')

    lightwave = property(_changing_off, "lightwave switch off module")







