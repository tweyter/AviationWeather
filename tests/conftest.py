import configparser
import os.path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine.url import URL
from sqlalchemy_utils.functions import database_exists, create_database
import pytest

from src.sql_classes import AirSigmet, Points


def base_url() -> URL:
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
    )
    return url


def verify_database(url: URL):
    if not database_exists(url):
        create_database(url)


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
    verify_database(url)
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
    verify_database(url)
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
