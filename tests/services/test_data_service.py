from datetime import datetime

import pytest
from medex.services.data import DataService
from medex.database_schema import CategoricalValueTable, NumericalValueTable, EntityTable
from medex.services.entity import EntityService
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session
from tests.mocks.filter_service import FilterServiceMock
from medex.dto.data import SortOrder, SortItem, SortDirection


@pytest.fixture
def setup_data(db_session):
    db_session.add_all([
        CategoricalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='diabetes', value='nein'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='diabetes', value='ja'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='follow up1', date_time=datetime(2022, 5, 15),
            key='diabetes', value='ja'
        ),
        NumericalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood pressure', value=129
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood pressure', value=138
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='follow up1', date_time=datetime(2022, 5, 15),
            key='blood pressure', value=135
        )
    ])
    db_session.commit()


@pytest.fixture
def filter_service_mock():
    yield FilterServiceMock()


def test_data_service_on_empty_database(db_session, filter_service_mock):
    service = DataService(
        database_session=db_session,
        filter_service=filter_service_mock,
        entity_service=EntityService(db_session)
    )
    actual_result, total = service.get_filtered_data_flat(
        entities=['diabetes'],
        measurements=['baseline'],
    )
    assert actual_result == []


def test_get_filtered_data_flat(db_session, filter_service_mock, setup_data):
    service = DataService(
        database_session=db_session,
        filter_service=filter_service_mock,
        entity_service=EntityService(db_session)
    )
    actual_result, total = service.get_filtered_data_flat(
        entities=['diabetes', 'blood pressure'],
        measurements=['baseline', 'follow up1'],
        limit=3,
        offset=2,
        sort_order=SortOrder(
            items=[
                SortItem(column='patient_id', direction=SortDirection.DESC),
                SortItem(column='key', direction=SortDirection.DESC),
            ]
        )
    )
    assert actual_result == [
        {'key': 'blood pressure', 'measurement': 'baseline', 'patient_id': 'p2', 'total': 6, 'value': '138'},
        {'key': 'blood pressure', 'measurement': 'follow up1', 'patient_id': 'p2', 'total': 6, 'value': '135'},
        {'key': 'diabetes', 'measurement': 'baseline', 'patient_id': 'p1', 'total': 6, 'value': 'nein'}
    ]
    assert total == 6

@pytest.fixture
def setup_numerical_data(db_session):
    db_session.add_all([
        EntityTable(key='blood pressure', type='Double'),
        NumericalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood pressure', value=90
        ),
        NumericalValueTable(
            patient_id='p3', case_id='c3', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood pressure', value=145
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood pressure', value=130
        ),
    ])
    db_session.commit()


def test_numerical_sorting_by_measurement(db_session, filter_service_mock, setup_numerical_data):
    service = DataService(
        database_session=db_session,
        filter_service=filter_service_mock,
        entity_service=EntityService(db_session)
    )
    actual_result, total = service.get_filtered_data_by_measurement(
        entities=['blood pressure'],
        measurements=['baseline', 'follow up1'],
        limit=10,
        offset=0,
        sort_order=SortOrder(
            items=[
                SortItem(column='blood pressure', direction=SortDirection.ASC),
            ]
        )
    )
    assert total == 3
    assert [float(x['blood pressure']) for x in actual_result] == [90, 130, 145]
