import pytest


def pytest_addoption(parser):
    group = parser.getgroup("Arguments to initialize instruments and devices")
    group.addoption("--product-type", help="Device type to calibrate and validate")
    group.addoption("--qual-station", help="Device type to calibrate and validate")
    group.addoption("--dut", help="Device under test")
