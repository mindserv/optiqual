import pytest
from station import Station, SupportedStations
from database import Station as StationTable, get_connection, get_session
from types import SimpleNamespace

DB_HOST = "localhost"  # or your database host
DB_PORT = 5432  # default PostgreSQL port
DB_USER = "postgres"
DB_PASSWORD = "postgres"

@pytest.fixture(scope='class')
def station(request):
    station_topology = SupportedStations.get_station_topology(request.config.option.qual_station)
    request.cls.station = Station(station_topology).initialize_station()
    yield

@pytest.fixture(scope='class')
def db(request):

    database = request.config.option.product_type
    db_client = get_connection(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, database)
    request.cls.db = db_client
    yield

@pytest.fixture(scope='class')
def db_session(request):
    database = request.config.option.product_type
    db_session = get_session(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, database)
    request.cls.db_session = db_session
    yield


@pytest.fixture(scope='class')
def artifacts(request):
    sn = request.config.option.dut_sn
    pn = request.config.option.dut_pn
    request.cls.artifacts = SimpleNamespace(sn=sn, pn=pn)
    yield