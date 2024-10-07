import pytest
from base_test import BaseTest


@pytest.mark.usefixtures("station")
class TestInstruments(BaseTest):
    """
    Sample test for demo purpose
    """
    @pytest.mark.dependency
    def test_instr_one(self):
        opm = self.station.tx_opm
        import pdb; pdb.set_trace()
        print(opm)
        print(opm.unit)
        print(opm.power)
        assert True

    @pytest.mark.dependency(depends=["TestInstruments::test_instr_one"])
    def test_instr_two(self):
        att = self.station.tx_attenuator
        print(att.output)
        att.output = 1
        print(att.output)
        print(att.attenuation)
        print(att.wavelength)
        att.wavelength = 1565
        print(att.wavelength)
        att.attenuation = 5
        print(att.attenuation)
        att.attenuation = 0
        print(att.attenuation)
        att.output = 0
        print(att.output)
        assert True
