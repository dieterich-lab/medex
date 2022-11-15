import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.models import create_tables, drop_tables


@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    create_tables()
    yield session
    drop_tables()
