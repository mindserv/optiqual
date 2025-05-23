import yaml
from instruments.instrument_base import InstrumentBase
import os

STATION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATION_CONFIG_PATH = os.path.join(STATION_DIR, "config", "station.yaml")




class SupportedStations(object):

    @classmethod
    def supported_stations(cls) -> yaml:
        with open(STATION_CONFIG_PATH) as station_config:
            return yaml.safe_load(station_config.read())

    @classmethod
    def get_station_topology(cls, station):
        all_stations = SupportedStations.supported_stations()
        return all_stations.get(station)


class Station(object):
    def __init__(self, station_topology):
        self.station_topology = station_topology
        self.instrument = InstrumentBase(self.station_topology)

    def initialize_station(self):
        return self.instrument.initialize_instrument()





