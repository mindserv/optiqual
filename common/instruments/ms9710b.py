from .instrument_driver_base import InstrumentDriverBase
import time

class ms9710b(InstrumentDriverBase):
    def __init__(self, *instr):
        self.instr = instr[0]

    def _configure_osa(self):
        self.instr.write('STA 1295')
        time.sleep(0.1)
        self.instr.write('CNT 1300')  # Center Wavelength
        time.sleep(0.1)
        self.instr.write('STO 1305')  # Stop Wavelength
        time.sleep(0.1)
        self.instr.write('RLV 0')  # Set reference level
        time.sleep(0.1)
        self.instr.write('LOG 10')  # Set scale, say log(/div)
        time.sleep(0.1)
        self.instr.write('ATT OFF')  # Set optical attenuation
        time.sleep(0.1)
        self.instr.write('RES 0.1')  # Set resolution
        time.sleep(0.1)
        self.instr.write('VBW 1KHz')  # Set videoBandwidth
        time.sleep(0.1)
        self.instr.write('AVT 10')  # Set Point Average
        time.sleep(0.1)
        self.instr.write('AVS 5')  # Set Sweep Average
        time.sleep(0.1)
        self.instr.write('SMT OFF')  # Set Smoothing Point
        time.sleep(0.1)
        self.instr.write('MPT 501')  # Set Sampling Points
        time.sleep(0.1)
        self.instr.write('ARES OFF')  # Set Actual-Resolution
        time.sleep(0.1)

    configure = property(_configure_osa, "optical spectrum analyzer")



    def _perform_single_sweep(self):
        self.instr.write('SSI')
        time.sleep(20)

    sweep = property(_perform_single_sweep, "single sweep")


    def _peak_search(self):
        self.instr.write('PKS PEAK')
        time.sleep(0.1)
        central_peak_wavelength = self.instr.query("CNT?")
        time.sleep(0.1)
        return float(central_peak_wavelength)

    peak = property(_peak_search, "cental peak wavelength")

    def _spectral_width_measurement_20db(self):
        self.instr.write("ANA THR, 20")
        time.sleep(0.2)
        spectral_20db = self.instr.query("ANAR?")
        spectral_width_20db = spectral_20db.strip().split(',')
        #rw = float(spectral_width_20db[0]), float(spectral_width_20db[1])
        return (f"{float(spectral_width_20db[0])}, {float(spectral_width_20db[1])}")

    threshold = property(_spectral_width_measurement_20db, "Threshold values")

    def _measure_smsr(self):
        self.instr.write("ANA SMSR, LEFT")
        time.sleep(0.1)
        second_peak = self.instr.query("ANAR?")
        smsr_values = second_peak.strip().split(',')
        #rd = float(smsr_values[0]), float(smsr_values[1])
        return (f"{float(smsr_values[0])}, {float(smsr_values[1])}")

    smsr = property(_measure_smsr, "Smsr values")

