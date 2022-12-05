import pytest
from modules.load_data_to_select import get_measurement
from modules.models import NameType, TableCategorical, TableNumerical
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


@pytest.fixture
def populate_data_3_measurements(db_session):
    db_session.add_all([
        NameType(orders=1, key='temperature', type='Double'),
        NameType(orders=2, key='diabetes', type='String'),

        TableCategorical(
            id=1, name_id='p1', case_id='case_p1', measurement='baseline', date='2015-03-05',
            key='diabetes', value='nein'
        ),
        TableCategorical(
            id=2, name_id='p2', case_id='case_p2', measurement='follow_up1', date='2015-04-05',
            key='diabetes', value='ja'
        ),

        TableNumerical(
            id=3, name_id='p1', case_id='case_p1', measurement='follow_up_z', date='2017-03-05',
            key='temperature', value=37.5
        ),
    ])
    db_session.commit()


@pytest.fixture
def populate_data_1_measurement(db_session):
    db_session.add_all([
        NameType(orders=1, key='temperature', type='Double'),
        NameType(orders=2, key='diabetes', type='String'),

        TableCategorical(
            id=1, name_id='p1', case_id='case_p1', measurement='x', date='2015-03-05',
            key='diabetes', value='nein'
        ),
        TableCategorical(
            id=2, name_id='p2', case_id='case_p2', measurement='x', date='2015-04-05',
            key='diabetes', value='ja'
        ),

        TableNumerical(
            id=3, name_id='p1', case_id='case_p1', measurement='x', date='2017-03-05',
            key='temperature', value=37.5
        ),
    ])
    db_session.commit()


def test_3_measurements(populate_data_3_measurements):
    assert get_measurement() == (['baseline', 'follow_up1', 'follow_up_z'], 'block')


def test_1_measurements(populate_data_1_measurement):
    assert get_measurement() == (['x'], 'none')
