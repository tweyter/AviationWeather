import configparser
import os.path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine.url import URL
from sql_classes import AirSigmet, Points
import pytest


@pytest.fixture(scope='session')
def engine():
    config = configparser.ConfigParser()
    config.read(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config.ini",
        )
    )
    url = URL(
        config['sqlalchemy']['drivername'],
        config['sqlalchemy']['username'],
        config['sqlalchemy']['password'],
        config['sqlalchemy']['host'],
        config['sqlalchemy']['port'],
        'test_database',
    )
    return create_engine(url)


@pytest.fixture(scope='session')
def sample_data_engine():
    config = configparser.ConfigParser()
    config.read(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config.ini",
        )
    )
    url = URL(
        config['sqlalchemy']['drivername'],
        config['sqlalchemy']['username'],
        config['sqlalchemy']['password'],
        config['sqlalchemy']['host'],
        config['sqlalchemy']['port'],
        'sample_data',
    )
    return create_engine(url)


@pytest.fixture(scope='session')
def tables(engine):
    AirSigmet.metadata.create_all(engine)
    Points.metadata.create_all(engine)
    yield
    AirSigmet.metadata.drop_all(engine)
    Points.metadata.drop_all(engine)


@pytest.fixture
def dbsession(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


@pytest.fixture
def db_sample(sample_data_engine):
    connection = sample_data_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
