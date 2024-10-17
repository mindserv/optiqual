import pytest
from station import Station, SupportedStations
from database import *

@pytest.fixture(scope='class')
def station(request):
    station_topology = SupportedStations.get_station_topology(request.config.option.qual_station)
    request.cls.station = Station(station_topology).initialize_station()
    yield

@pytest.fixture(scope='class')
def db(request):
    user = "postgres"
    password = "postgres"
    host = "localhost"  # or your database host
    port = 5432  # default PostgreSQL port
    database = request.config.option.product_type
    db_client = get_postgres_connection(user, password, host, port, database)
    request.cls.db = db_client
    yield

@pytest.fixture(scope='class')
def test_properties(request):
    dut = request.config.option.dut
    pn = request.config.option.product_type
    yield