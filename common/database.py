import enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float

# TODO: Database name, database server has be abstracted
engine = create_engine('postgresql://localhost/cpx100g')


def get_connection(user, password, host, port, database):
    """
    Create a connection to a PostgreSQL database using SQLAlchemy.

    :param user: Database username
    :param password: Database password
    :param host: Host where the database is located
    :param port: Port number for the database (default is 5432)
    :param database: Name of the database to connect
    :return: SQLAlchemy engine object to connect

    """
    # Create the database URL
    database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    # Create an engine
    engine = create_engine(database_url)

    return engine

def get_session(user, password, host, port, database):
    """
    Create a connection to a PostgreSQL database using SQLAlchemy.

    :param user: Database username
    :param password: Database password
    :param host: Host where the database is located
    :param port: Port number for the database (default is 5432)
    :param database: Name of the database to connect
    :return: SQLAlchemy session object
    """

    engine = get_connection(user, password, host, port, database)

    Base.metadata.create_all(engine)

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # Create a session
    session = Session()

    return session


class TestStatus(object):
    PASS = "pass"
    FAIL = "fail"
    INCOMPLETE = "incomplete"
    ABORT = "abort"


# Base tables

Base = declarative_base()


class TestResults(Base):
    __tablename__ = 'test_results'

    id = Column(Integer, primary_key=True)
    dut_id = Column(Integer, ForeignKey('dut.id'))
    test_name = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    station_id = Column(Integer, ForeignKey('station.id'))
    config_file = Column(String)
    results_html_file = Column(String)
    results_csv_file = Column(String)
    user = Column(String)
    comments = Column(String)  # User comments about the test
    pass_fail = Column(String, nullable=False)
    dut_sw_version = Column(String)


class Dut(Base):
    __tablename__ = 'dut'
    id = Column(Integer, primary_key=True)
    dut_sn = Column(String, nullable=False, unique=True)
    dut_part_num = Column(String, nullable=False)
    dut_part_num_rev = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)


class Station(Base):
    __tablename__ = 'station'
    id = Column(Integer, primary_key=True)
    station_name = Column(String, nullable=False)
    station_description = Column(String, nullable=False)

class DummyRxAccuracy(Base):
    __tablename__ = 'dummy_rx_accuracy'
    id = Column(Integer, primary_key=True)
    test_results_id = Column(Integer, ForeignKey('test_results.id'))
    wavelength = Column(Float)
    rx_power = Column(Float)
    attenuation = Column(Float)

class TestSweeps(Base):
    __tablename__ = 'test_sweeps'
    id = Column(Integer, primary_key=True)
    test_results_id = Column(Integer, ForeignKey('test_results.id'))
    wavelength = Column(Float)
    rx_power = Column(Float)
    attenuation = Column(Float)


if __name__ == '__main__':
    user = "postgres"
    password = "postgres"
    host = "localhost"  # or your database host
    port = 5432  # default PostgreSQL port
    database = "cpx100g"

    session = get_session(user, password, host, port, database)

    # Now you can use the session to interact with the database
    try:
        # Example query (replace with your actual queries)
        result = session.execute(text("SELECT 1"))
        for row in result:
            print(row)
    finally:
        # Close the session when done
        session.close()
