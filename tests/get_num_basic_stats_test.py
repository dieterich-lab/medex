from modules.models import TableNumerical, Patient, NameType
from modules.get_data_to_basic_stats import get_num_basic_stats


def test_it(db_session):
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
    df, error = get_num_basic_stats(['Bmi'], ['1'], (1, 1, 0), {'selected': None}, {'filter_update': 0}, db_session)
    assert df.shape[0] == 1

