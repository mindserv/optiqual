from .instrument_driver_base import InstrumentDriverBase


class hp81635a(InstrumentDriverBase):
    def __init__(self, *instr):
        pass

    def get_power(self):
        power = 12.5
        print(f'succeeded reading power {power}')
        return power
