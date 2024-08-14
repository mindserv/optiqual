import pytest
from base_test import BaseTest


@pytest.mark.usefixtures("station")
class TestInstruments(BaseTest):
    """
    Sample test for demo purpose
    """
    @pytest.mark.dependency
    def test_instr_one(self):
        assert True

    @pytest.mark.dependency(depends=["TestInstruments::test_instr_one"])
    def test_instr_two(self):
        print(self.execute_example())
        assert True
