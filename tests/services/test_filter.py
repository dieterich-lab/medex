import pytest
from sqlalchemy.orm import Query, InstrumentedAttribute

from medex.dto.filter import FilterStatus, NumericalFilter
from medex.services.session import SessionService
from modules.models import Patient, NameType, TableCategorical, TableNumerical, \
    SessionFilteredNameIds
from medex.services.filter import FilterService


@pytest.fixture
def populate_data(db_session):
    db_session.add_all([
        Patient(name_id='p1', case_id='case_p1'),
        Patient(name_id='p2', case_id='case_p2'),
        NameType(orders=1, key='temperature', type='Double'),
        NameType(orders=2, key='diabetes', type='String'),
        NameType(orders=3, key='blood pressure', type='Double'),
        TableCategorical(
            id=1, name_id='p1', case_id='case_p1', measurement='baseline', date='2015-03-05',
            key='diabetes', value='nein'
        ),
        TableCategorical(
            id=2, name_id='p2', case_id='case_p2', measurement='baseline', date='2015-04-05',
            key='diabetes', value='ja'
        ),
        TableNumerical(
            id=3, name_id='p1', case_id='case_p1', measurement='baseline', date='2015-03-05',
            key='temperature', value=37.5
        ),
        TableNumerical(
            id=4, name_id='p2', case_id='case_p2', measurement='baseline', date='2015-04-05',
            key='temperature', value=40.7
        ),
        TableNumerical(
            id=5, name_id='p1', case_id='case_p1', measurement='baseline', date='2015-03-05',
            key='blood pressure', value=135
        ),
    ])
    db_session.commit()


@pytest.fixture
def filter_status():
    return FilterStatus(filters=[])


MY_SESSION_ID = 'my_session_id'


class SessionServiceMock(SessionService):

    def __init__(self):  # noqa
        pass

    def touch(self):
        pass

    def get_id(self):
        return MY_SESSION_ID


@pytest.fixture
def session_service():
    yield SessionServiceMock()


@pytest.fixture
def filter_service(db_session, filter_status, session_service):
    yield FilterService(
        database_session=db_session,
        filter_status=filter_status,
        session_service=session_service
    )


def get_result_set_as_dict(query: Query):
    columns = []
    for item in query.column_descriptions:
        for name, value in item['entity'].__dict__.items():
            if isinstance(value, InstrumentedAttribute):
                columns.append(name)
    result_set = query.all()
    return [
        {col: row.__dict__[col] for col in columns}
        for row in result_set
    ]


def test_numerical_filter(filter_service: FilterService, db_session, populate_data):
    new_filter = NumericalFilter(from_value=39, to_value=43, min=30, max=43)
    filter_service.add_filter(entity='temperature', new_filter=new_filter)
    assert len(filter_service._filter_status.filters) == 1
    actual = get_result_set_as_dict(
        db_session.query(SessionFilteredNameIds)
    )
    expected = [{'session_id': MY_SESSION_ID, 'name_id': 'p2'}]
    assert actual == expected
