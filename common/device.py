import yaml
import os

#DEVICE_CONFIG_PATH = "config/device.yaml"

DIR_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEVICE_CONFIG_FILE = os.path.join(DIR_PATH, "config", "device.yaml")

class SupportedDevices(object):

    @classmethod
    def supported_devices(cls):
        #DEVICE_CONFIG_FILE = "{}/device.yaml".format(device_config_path)
        print("======================")
        devices = list()
        with open(DEVICE_CONFIG_FILE) as device_config:
            device_dict = yaml.safe_load(device_config.read())
            for dev in device_dict.get('supported_devices'):
                devices.append(dev.get('product_type'))
            return devices

