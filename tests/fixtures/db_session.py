import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from medex.database_schema import create_tables, drop_tables
from medex.services.database import init_db


@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    init_db(engine, lambda: session)
    create_tables()
    yield session
    drop_tables()
