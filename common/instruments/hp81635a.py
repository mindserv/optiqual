from .instrument_driver_base import InstrumentDriverBase


class hp81635a(InstrumentDriverBase):
    def __init__(self, *instr):

        self.instr = instr[0]
        self.chassis = int(instr[1]['chassis'])
        self.slot = int(instr[1]['slot'])
        self.subslot = int(instr[1]['sub_slot'])
        self._currentunit = self._get_unit()
        self.unit = 'dBm'
        self.wavelength = 1550.0
        self.averaging_time = 0.5
        pass

    def _set_unit(self, unit):
        assert unit in ("dBm", "DBM", "Watts", "W")
        self.instr.write(':SENSE%d:CHAN%d:POW:UNIT %s' % (self.slot, self.subslot, unit))
        self._currentunit = self._get_unit()

    def _get_unit(self):
        val = int(self.instr.query(':SENSE%d:CHAN%d:POW:UNIT?' % (self.slot, self.subslot)))
        if val == 0:
            return "dBm"
        elif val == 1:
            return "W"

    unit = property(_get_unit, _set_unit, None, "Measurement unit: dBm or Watts")

    def _set_wavelength(self, wl):
        wl = wl * 1e-9
        self.instr.write(':SENSE%d:CHAN%d:POW:WAV %sM' % (self.slot, self.subslot, wl))

    def _get_wavelength(self):
        val = self.instr.query(':SENSE%d:CHAN%d:POW:WAV?' % (self.slot, self.subslot))
        return eval(val)

    wavelength = property(_get_wavelength, _set_wavelength, None, "Wavelength in M")

    def _set_averaging(self, tm):
        #if self.is_master():
        self.instr.write(':SENSE%d:CHAN%d:POW:ATIM %sS' % (self.slot, self.subslot, tm))

    def _get_averaging(self):
        val = self.instr.query(':SENSE%d:CHAN%d:POW:ATIM?' % (self.slot, self.subslot))
        return val

    averaging_time = property(_get_averaging, _set_averaging, None, "Averaging time in S")

    def _get_power(self):
        try:
            val = self.instr.query(':FETCH%d:CHAN%d:SCAL:POW?' % (self.slot, self.subslot))
            val = float(val)
            if (val > 1000.0):
                val = -99.0
        except:
            print
            "raised exception while reading the power from powerMeter so, attempting one more time"
            try:
                val = self.instr.query(':FETCH%d:CHAN%d:SCAL:POW?' % (self.slot, self.subslot))
                val = float(val)
                if (val > 1000.0):
                    val = -99.0
            except:
                print
                "Raised exception while reading the Power from powermeter!!!"
        return float(val)

    power = property(_get_power, None, None, "Power in current units.")

