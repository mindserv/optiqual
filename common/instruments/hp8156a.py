from .instrument_driver_base import InstrumentDriverBase


class hp8156a(InstrumentDriverBase):
    def __init__(self, *instr):
        self.instr = instr[0]
        self.wavelength = 1550.0
        print("eqpt IDN response -> %s" % (self.instr.query("*IDN?")))

    def _get_attenuation(self):
        raw = self.instr.query(":INP:ATT?")
        return float(raw)

    def _set_attenuation(self, atten):
        self.instr.write(":INP:ATT %.2f" % (atten,))

    def _no_attenuation(self):
        self.instr.write(":INP:ATT MIN")

    attenuation = property(_get_attenuation, _set_attenuation, _no_attenuation, "attenuation factor (dB)")

    def _get_max(self):
        raw = self.instr.query(":INP:ATT? MAX")
        return raw

    maximum_attenuation = property(_get_max, None, None, "Maximum possible attenuation.")

    def _get_min(self):
        raw = self.instr.query(":INP:ATT? MIN")
        return raw

    minimum_attenuation = property(_get_min, None, None, "Minimum possible attenuation.")

    def _get_wavelength(self):
        raw = self.instr.query(":INP:WAV?")  # in meters
        return raw

    def _set_wavelength(self, wl):
        #wl = wl * 1e-9
        self.instr.write(":INP:WAV %s NM" % (wl,))

    wavelength = property(_get_wavelength, _set_wavelength, None, "wavelengh in nM")

    def _get_output(self):
        return int(self.instr.query(":OUTP:STAT?"))

    def _set_output(self, flag):
        self.instr.write(":OUTP:STAT %s" % (flag,))

    output = property(_get_output, _set_output, None, "state of output shutter")

    def on(self):
        self._set_output("ON")

    def off(self):
        self._set_output("OFF")

    def setAttnSpeed(self, input=1, value=12.0):
        self.instr.write(":INP%s:ATT:SPE %d" % (input, value))

    def getAttnSpeed(self, input=1):
        return self.query(":INP%s:ATT:SPE?" % (input))

