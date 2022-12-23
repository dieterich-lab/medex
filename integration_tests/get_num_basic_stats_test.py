from modules.models import TableNumerical, Patient, NameType
from modules.get_data_to_basic_stats import get_num_basic_stats
# noinspection PyUnresolvedReferences
from integration_tests.fixtures.db_session import db_session
# noinspection PyUnresolvedReferences
from tests.fixtures.services import session_service, filter_service, filter_status


# Unfortunately get_num_basic_stats() uses SQL functions like
# 'stddev' not available easily sqlite. So we need a Postgres
# database to run it.


def test_it(db_session, filter_service):
    db_session.add(Patient(
        name_id='a',
        case_id='b',
    ))
    db_session.add(NameType(
        orders=1,
        key='Bmi',
        type='Double',
    ))
    db_session.add(TableNumerical(
        id=1,
        name_id='a',
        case_id='b',
        measurement='baseline',
        date='2020-11-05',
        time='01:30:30',
        key='Bmi',
        value=19,
    ))
    db_session.commit()
    db_session.rollback()
    db_session.close()
    df, error = get_num_basic_stats(['Bmi'], ['baseline'], (1, 1, 0), {'selected': None}, filter_service)
    assert df.shape[0] == 1
