import enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float

# TODO: Database name, database server has be abstracted
engine = create_engine('postgresql://localhost/cpx100g')


def get_postgres_connection(user, password, host, port, database):
    """
    Create a connection to a PostgreSQL database using SQLAlchemy.

    :param user: Database username
    :param password: Database password
    :param host: Host where the database is located
    :param port: Port number for the database (default is 5432)
    :param database: Name of the database to connect to
    :return: SQLAlchemy session object
    """

    # Create the database URL
    database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    # Create an engine
    engine = create_engine(database_url)

    Base.metadata.create_all(engine)

    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

    # Create a session
    session = Session()

    return session


class TestStatus(enum.Enum):
    P = "pass"
    F = "fail"
    I = "incomplete"
    A = "abort"


# Base tables

Base = declarative_base()


class TestResults(Base):
    __tablename__ = 'test_results'

    Id = Column(Integer, primary_key=True)
    DutSN = Column(Integer, ForeignKey('dut.Id'))
    PartNum = Column(String, nullable=False)
    TestName = Column(String, nullable=False)
    StartTime = Column(DateTime, nullable=False)
    EndTime = Column(DateTime, nullable=False)
    StationID = Column(Integer, ForeignKey('station.Id'))
    TestScript = Column(String, nullable=False)
    ConfigFile = Column(String)
    ResultsHtmlFile = Column(String)
    ResultsCsvFile = Column(String)
    User = Column(String)
    Comments = Column(String)  # User comments about the test
    PassFail = Column(Enum(TestStatus), nullable=False)
    DutSwVersion = Column(String)


class Dut(Base):
    __tablename__ = 'dut'
    Id = Column(Integer, primary_key=True)
    DutSN = Column(String, nullable=False, unique=True)
    DutPartNum = Column(String, nullable=False)
    DutPartNumRev = Column(String, nullable=False)
    Date = Column(DateTime, nullable=False)


class Station(Base):
    __tablename__ = 'station'
    Id = Column(Integer, primary_key=True)
    StationName = Column(String, nullable=False)
    StationDescription = Column(String, nullable=False)

class DummyRxAccuracy(Base):
    __tablename__ = 'dummy_rx_accuracy'
    Id = Column(Integer, primary_key=True)
    TestResultsId = Column(Integer, ForeignKey('test_results.Id'))
    Wavelength = Column(Float)
    RxPower = Column(Float)
    Attenuation = Column(Float)


if __name__ == '__main__':
    user = "postgres"
    password = "postgres"
    host = "localhost"  # or your database host
    port = 5432  # default PostgreSQL port
    database = "cpx100g"

    session = get_postgres_connection(user, password, host, port, database)

    # Now you can use the session to interact with the database
    try:
        # Example query (replace with your actual queries)
        result = session.execute(text("SELECT 1"))
        for row in result:
            print(row)
    finally:
        # Close the session when done
        session.close()
