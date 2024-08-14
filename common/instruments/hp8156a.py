from .instrument_driver_base import InstrumentDriverBase


class hp8156a(InstrumentDriverBase):
    def __init__(self, instr):
        pass

    def set_atten(self, attn):
        print(f'Setting attenuation to {attn}')
        return True
