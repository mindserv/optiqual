import pytest


def pytest_addoption(parser):
    group = parser.getgroup("Arguments to initialize instruments and devices")
    group.addoption("--product-type", help="Device type to calibrate and validate")
    group.addoption("--qual-station", help="Device type to calibrate and validate")
    group.addoption("--dut-sn", help="SN of Device under test")
    group.addoption("--dut-pn", help="PN of Device under test")
