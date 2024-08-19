import yaml
import pyvisa
import sys
import os

from types import SimpleNamespace

# TODO: Fix the . notation by setting the path correctly.
from .hp81635a import hp81635a
from .hp8156a import hp8156a
#import pdb; pdb.set_trace()
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))#os.path.dirname(os.path.dirname(os.path.abspath(__file__), '..'))
INSTRUMENT_CONFIG_FILE = os.path.join(BASE_DIR, "config", "instrument.yaml")#"/Users/kathir/mydev/optiqual/config/instrument.yaml"
GPIB = 'GPIB'
I2C = 'I2C'


class SupportedInstruments(object):

    @classmethod
    def supported_instruments(cls):
        instruments = list()
        with open(INSTRUMENT_CONFIG_FILE) as instrument_config:
            return yaml.safe_load(instrument_config.read())

    @classmethod
    def construct_instrument_connector(cls):
        pass


class NestedNamespace(SimpleNamespace):
    def __init__(self, dictionary, **kwargs):
        """
        Helper class to access dict key/values using dot notation
        Example,
        {'name': 'optiqual1',
        'devices': ['10G_LR', '10G_SR'],
        'tx_attenuator': <instruments.hp8156a.hp8156a object at 0x102159310>,
        'rx_attenuator': 'None'}
        can  be accessed as,
        obj.tx_attenuator, where obj is instance of this class

        :param dictionary: dict of values
        :param kwargs: kwargs format.
        """
        super().__init__(**kwargs)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__setattr__(key, NestedNamespace(value))
            elif isinstance(value, list):
                self.__setattr__(key, map(NestedNamespace, value))
            else:
                self.__setattr__(key, value)
def instantiate_module_obj(instr_model):
    try:
        return getattr(sys.modules[__name__], instr_model.lower())
    except AttributeError:
        print("Module not found")
        raise


class InstrumentBase(object):
    def __init__(self, station_topology):
        self.station_topology = station_topology
        self.all_instruments = SupportedInstruments.supported_instruments().get('supported_instruments')

    def instruments_in_station(self):
        station_instr = list()
        for instr in self.all_instruments:
            if instr.get('station_name') == self.station_topology.get('name'):
                station_instr.append(instr)
        return station_instr

    def initialize_instrument(self):
        for instr in self.instruments_in_station():
            #import pdb; pdb.set_trace()
            if instr.get('interface') == GPIB:
                resource_manager = pyvisa.ResourceManager()
                addr = f'{instr.get('interface')}0::{instr.get('gpib_addr')}::INSTR'
                # TODO: Setup instruments in Windows if MAC doesn't work
                init_rm = resource_manager.open_resource(addr)
                instr_obj = instantiate_module_obj(instr.get('model').lower())(init_rm, instr)
                # Get station instrument key from the values, values are retrieved from supported_instruments already
                # mapped to the station
                station_instr_val = [*self.station_topology.values()]
                station_instr_key = [*self.station_topology.keys()]
                if instr.get('instrument_name') in station_instr_val:
                    index = station_instr_val.index(instr.get('instrument_name'))
                    instr_name = station_instr_key[index]
                    self.station_topology.update({instr_name: instr_obj})
        station_info = NestedNamespace(self.station_topology)
        return station_info
