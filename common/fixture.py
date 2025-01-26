import pytest
from station import Station, SupportedStations
from database import Station as StationTable, get_connection, get_session
from types import SimpleNamespace
# from instruments.sub20_driver import Sub20Driver

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


@pytest.fixture(scope='class')
def sub20(request):
    #sub20 = Sub20Driver()
    sub20 = "test"
    request.cls.sub20 = sub20
    yield

@pytest.fixture(scope="class")
def add_custom_data(request):
    # Initialize a dictionary at the class level
    if not hasattr(request.cls, "custom_data"):
        request.cls.custom_data = {}

    def _add_data(key, value):
        # Add custom data to the class-level dictionary
        request.cls.custom_data[key] = value

    return _add_data