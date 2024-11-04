import pytest
from base_test import BaseTest


@pytest.mark.usefixtures("station")
class TestInstruments(BaseTest):
    """
    Sample test for demo purpose
    """
    @pytest.mark.dependency
    def test_instr_one(self):
        """
        opm = self.station.tx_opm
        self.log.info(opm)
        self.log.info(opm.unit)
        self.log.info(opm.power)
        """
        assert True

    """
    @pytest.mark.dependency(depends=["TestInstruments::test_instr_one"])
    def test_instr_two(self):
        att = self.station.tx_attenuator
        self.log.info("Attenuator Status %d" % att.output)
        att.output = 1
        self.log.info("Attenuator Status %d" % att.output)
        self.log.info("Attenuation: %.f" % att.attenuation)
        self.log.info("Current WL: %s" % att.wavelength)
        att.wavelength = 1545
        self.log.info("Wavelength is set to %f" % (1545.0))
        self.log.info("Attenuator WL: %s" % att.wavelength)
        att.attenuation = 5
        self.log.info("Attenuation: %.f" % att.attenuation)
        att.attenuation = 0
        self.log.info("Attenuation: %.f" % att.attenuation)
        att.output = 0
        self.log.info("Attenuator Status %d" % att.output)
        assert True
    """
