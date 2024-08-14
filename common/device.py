import yaml

#DEVICE_CONFIG_PATH = "config/device.yaml"

DEVICE_CONFIG_FILE = "/Users/kathir/mydev/optiqual/config/device.yaml"

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

