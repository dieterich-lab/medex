import pytest
from medex.services.data import DataService
from modules.models import TableCategorical, TableNumerical
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session
from tests.mocks.filter_service import FilterServiceMock
from medex.dto.data import SortOrder, SortItem, SortDirection


@pytest.fixture
def setup_data(db_session):
    db_session.add_all([
        TableCategorical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='diabetes', value='nein'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-05-15', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-05-15', key='diabetes', value='ja'
        ),
        TableNumerical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='blood pressure', value=129
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-05-15', key='blood pressure', value=138
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-05-15', key='blood pressure', value=135
        )
    ])
    db_session.commit()


@pytest.fixture
def filter_service_mock():
    yield FilterServiceMock()


def test_data_service_simple(db_session, filter_service_mock):
    service = DataService(
        database_session=db_session,
        filter_service=filter_service_mock
    )
    actual_result, total = service.get_filtered_data_flat(
        entities=['diabetes'],
        measurements=['baseline'],
    )
    assert actual_result == []


def test_get_filtered_data_flat(db_session, filter_service_mock, setup_data):
    service = DataService(
        database_session=db_session,
        filter_service=filter_service_mock
    )
    actual_result, total = service.get_filtered_data_flat(
        entities=['diabetes', 'blood pressure'],
        measurements=['baseline', 'follow up1'],
        limit=3,
        offset=2,
        sort_order=SortOrder(
            items=[
                SortItem(column='name_id', direction=SortDirection.DESC),
                SortItem(column='key', direction=SortDirection.DESC),
            ]
        )
    )
    assert actual_result == [
        {'key': 'blood pressure', 'measurement': 'baseline', 'name_id': 'p2', 'total': 6, 'value': '138'},
        {'key': 'blood pressure', 'measurement': 'follow up1', 'name_id': 'p2', 'total': 6, 'value': '135'},
        {'key': 'diabetes', 'measurement': 'baseline', 'name_id': 'p1', 'total': 6, 'value': 'nein'}
    ]
    assert total == 6
