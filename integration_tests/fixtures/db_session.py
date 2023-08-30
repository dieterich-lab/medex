from time import sleep
from os import environ

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from medex.database_schema import create_tables, drop_tables
from medex.services.database import init_db


POSTGRES_USER = 'test'
POSTGRES_PASSWORD = 'test'
POSTGRES_DB = 'example'
POSTGRES_PORT = 5477
POSTGRES_HOST = 'localhost'


@pytest.fixture
def db_session():
    _setup_environment()
    session = _get_db_session()
    create_tables()
    yield session
    session.close()


@pytest.fixture
def db_session_clean():
    _setup_environment()
    session = _get_db_session()
    yield session
    session.close()


def _setup_environment():
    environ['POSTGRES_USER'] = POSTGRES_USER
    environ['POSTGRES_PASSWORD'] = POSTGRES_PASSWORD
    environ['POSTGRES_HOST'] = POSTGRES_HOST
    environ['POSTGRES_DB'] = POSTGRES_DB
    environ['POSTGRES_PORT'] = str(POSTGRES_PORT)


def _get_db_session():
    retry_count = 0
    while True:
        try:
            engine = create_engine(
                f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
            )
            session_maker = sessionmaker(bind=engine)
            session = session_maker()
            init_db(engine, lambda: session)
            drop_tables()
            return session
        except Exception as e:
            retry_count += 1
            if retry_count >= 5:
                raise Exception('Failed to connect to Postgres: ' + str(e))
            print(f"Postgres not responding - retying ({retry_count})")
            sleep(1)
