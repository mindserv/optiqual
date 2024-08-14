import pytest
from station import Station, SupportedStations


@pytest.fixture(scope='class')
def station(request):
    station_topology = SupportedStations.get_station_topology(request.config.option.qual_station)
    request.cls.station = Station(station_topology).initialize_station()
    yield
