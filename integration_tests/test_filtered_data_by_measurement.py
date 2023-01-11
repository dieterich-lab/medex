import pytest
from medex.services.data import DataService
from modules.models import TableCategorical, TableNumerical, NameType
# noinspection PyUnresolvedReferences
from integration_tests.fixtures.db_session import db_session
from tests.mocks.filter_service import FilterServiceMock
from medex.dto.data import SortOrder, SortItem, SortDirection


@pytest.fixture
def setup_data_new(db_session):
    db_session.add_all([
        NameType(orders=1, key='diabetes', type='String'),
        NameType(orders=2, key='blood pressure', type='Double'),
        TableCategorical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='diabetes', value='nein'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-05-15', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-05-15', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p3', case_id='c3', measurement='baseline', date='2021-05-20', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p3', case_id='c3', measurement='follow up1', date='2022-05-20', key='diabetes', value='nein'
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


# Unfortunately get_filtered_data_by_measurement() uses SQL functions like
# 'string_agg' which is not available easily in sqlite. So we need a Postgres
# database to run it with some modifications

def test_get_filtered_data_by_measurement(db_session, filter_service_mock, setup_data_new):
    service = DataService(
        database_session=db_session,
        filter_service=filter_service_mock
    )
    actual_result, total = service.get_filtered_data_by_measurement(
        entities=['diabetes', 'blood pressure'],
        measurements=['baseline', 'follow up1'],
        limit=4,
        offset=1,
        sort_order=SortOrder(
            items=[
                SortItem(column='name_id', direction=SortDirection.DESC),
                SortItem(column='diabetes', direction=SortDirection.DESC),
                SortItem(column='blood pressure', direction=SortDirection.ASC),
            ]
        )
    )
    assert actual_result == [
        {'blood pressure': None, 'diabetes': 'ja', 'measurement': 'baseline', 'name_id': 'p3', 'total': 5},
        {'blood pressure': '135', 'diabetes': 'ja', 'measurement': 'follow up1', 'name_id': 'p2', 'total': 5},
        {'blood pressure': '138', 'diabetes': 'ja', 'measurement': 'baseline', 'name_id': 'p2', 'total': 5},
        {'blood pressure': '129', 'diabetes': 'nein', 'measurement': 'baseline', 'name_id': 'p1', 'total': 5}
    ]
    assert total == 5
