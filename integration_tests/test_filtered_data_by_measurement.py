from datetime import datetime

import pytest
from medex.services.data import DataService
from medex.database_schema import CategoricalValueTable, NumericalValueTable, EntityTable
# noinspection PyUnresolvedReferences
from integration_tests.fixtures.db_session import db_session
from medex.services.entity import EntityService
from tests.mocks.filter_service import FilterServiceMock
from medex.dto.data import SortOrder, SortItem, SortDirection


@pytest.fixture
def setup_data_new(db_session):
    db_session.add_all([
        EntityTable(key='diabetes', type='String'),
        EntityTable(key='blood pressure', type='Double'),
    ])
    db_session.commit()
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
        CategoricalValueTable(
            patient_id='p3', case_id='c3', measurement='baseline', date_time=datetime(2021, 5, 20),
            key='diabetes', value='ja'
        ),
        CategoricalValueTable(
            patient_id='p3', case_id='c3', measurement='follow up1', date_time=datetime(2022, 5, 20),
            key='diabetes', value='nein'
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


# Unfortunately get_filtered_data_by_measurement() uses SQL functions like
# 'string_agg' which is not available easily in sqlite. So we need a Postgres
# database to run it with some modifications

def test_get_filtered_data_by_measurement(db_session, filter_service_mock, setup_data_new):
    service = DataService(
        database_session=db_session,
        filter_service=filter_service_mock,
        entity_service=EntityService(db_session),
    )
    actual_result, total = service.get_filtered_data_by_measurement(
        entities=['diabetes', 'blood pressure'],
        measurements=['baseline', 'follow up1'],
        limit=4,
        offset=1,
        sort_order=SortOrder(
            items=[
                SortItem(column='patient_id', direction=SortDirection.DESC),
                SortItem(column='diabetes', direction=SortDirection.DESC),
                SortItem(column='blood pressure', direction=SortDirection.ASC),
            ]
        )
    )
    assert actual_result == [
        {'blood pressure': None, 'diabetes': 'ja', 'measurement': 'baseline', 'patient_id': 'p3', 'total': 5},
        {'blood pressure': '135', 'diabetes': 'ja', 'measurement': 'follow up1', 'patient_id': 'p2', 'total': 5},
        {'blood pressure': '138', 'diabetes': 'ja', 'measurement': 'baseline', 'patient_id': 'p2', 'total': 5},
        {'blood pressure': '129', 'diabetes': 'nein', 'measurement': 'baseline', 'patient_id': 'p1', 'total': 5}
    ]
    assert total == 5
