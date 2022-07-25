from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool
from modules.models import Base, TableNumerical, Patient, NameType
from modules.get_data_to_basic_stats import get_num_basic_stats


@fixture
def session(postgresql):
    connection = f'postgresql+psycopg2://{postgresql.info.user}:@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}'
    engine = create_engine(connection, echo=False, pool_pre_ping=True, poolclass=NullPool)
    c = engine.connect()
    Base.metadata.create_all(engine)
    yield Session(engine)
    c.connection.connection.close()

def test_it(session):
    session.add(Patient(
        name_id='a',
        case_id='b',
    ))
    session.add(NameType(
        orders=1,
        key='Bmi',
        type='Double',
    ))
    session.add(TableNumerical(
        id=1,
        name_id='a',
        case_id='b',
        measurement=1,
        date='2020-11-05',
        time='01:30:30',
        key='Bmi',
        value=19,
    ))
    session.commit()
    session.rollback()
    session.close()
    df, error = get_num_basic_stats(['Bmi'], ['1'], (1, 1, 0), {'selected': None}, {'filter_update': 0}, session)
    assert df.shape[0] == 1

