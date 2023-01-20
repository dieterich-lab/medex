from time import sleep

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modules.models import create_tables, drop_tables
from medex.services.database import init_db


@pytest.fixture
def db_session():
    retry_count = 0
    while True:
        try:
            engine = create_engine('postgresql://test:test@localhost:5477/example')
            session_maker = sessionmaker(bind=engine)
            session = session_maker()
            init_db(engine, lambda: session)
            drop_tables()
            create_tables()
            break
        except Exception as e:
            retry_count += 1
            if retry_count >= 5:
                raise Exception('Failed to connect to Postgres: ' + str(e))
            print(f"Postgres not responding - retying ({retry_count})")
            sleep(1)
    yield session
    session.close()
