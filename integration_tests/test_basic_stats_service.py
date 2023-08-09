from datetime import datetime

import pytest
from medex.dto.basic_stats import BasicStatsNumericalDataRequest
from medex.services.basic_stats import BasicStatisticsService
from medex.database_schema import NumericalValueTable, EntityTable, PatientTable, CategoricalValueTable
from tests.mocks.filter_service import FilterServiceMock
# noinspection PyUnresolvedReferences
from integration_tests.fixtures.db_session import db_session


@pytest.fixture
def setup_basic_stats_data_minimal(db_session):
    db_session.add_all([
        PatientTable(patient_id='p1', case_id='c1'),
        EntityTable(key='blood pressure', type='Double'),
        NumericalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='blood pressure', value=129
        ),
    ])
    db_session.commit()


@pytest.fixture
def setup_basic_stats_data(db_session):
    db_session.add_all([
        PatientTable(patient_id='p1', case_id='c1'),
        PatientTable(patient_id='p2', case_id='c2'),
        PatientTable(patient_id='p3', case_id='c3'),
        EntityTable(key='blood pressure', type='Double'),
        EntityTable(key='temperature', type='Double'),
        EntityTable(key='diabetes', type='String'),
        EntityTable(key='biopsy', type='String'),
    ])
    db_session.commit()
    db_session.add_all([
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
        ),
        NumericalValueTable(
            patient_id='p3', case_id='c3', measurement='baseline', date_time=datetime(2021, 9, 27),
            key='temperature', value=38.5
        ),
        NumericalValueTable(
            patient_id='p3', case_id='c3', measurement='follow up1', date_time=datetime(2022, 9, 27),
            key='temperature', value=41.5
        ),
        CategoricalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 4, 15),
            key='diabetes', value='nein'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 7, 21),
            key='diabetes', value='ja'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='follow up1', date_time=datetime(2022, 5, 15),
            key='diabetes', value='ja'
        ),
        CategoricalValueTable(
            patient_id='p3', case_id='c3', measurement='baseline', date_time=datetime(2022, 3, 9),
            key='biopsy', value='ja'
        ),
    ])
    db_session.commit()


@pytest.fixture
def filter_service_mock():
    yield FilterServiceMock()


def test_get_basic_stats_for_numerical_entities(setup_basic_stats_data, db_session, filter_service_mock):
    service = BasicStatisticsService(db_session, filter_service_mock)
    basic_stats_data = _get_parsed_data_numerical()
    actual_result = service.get_basic_stats_for_numerical_entities(basic_stats_data)
    assert len(actual_result) == 4
    assert actual_result[0]['count'] == 2
    assert len(actual_result[0]) == 10


def test_get_basic_stats_for_categorical_entities(setup_basic_stats_data, db_session, filter_service_mock):
    service = BasicStatisticsService(db_session, filter_service_mock)
    basic_stats_data = _get_parsed_data_categorical()
    actual_result = service.get_basic_stats_for_categorical_entities(basic_stats_data)
    assert len(actual_result) == 3
    assert actual_result[0]['count NaN']
    assert len(actual_result[0]) == 4


def test_get_basic_stats_for_numerical_entities_minimal(
        setup_basic_stats_data_minimal, db_session, filter_service_mock
):
    service = BasicStatisticsService(db_session, filter_service_mock)
    basic_stats_data = _get_parsed_data_numerical()
    actual_result = service.get_basic_stats_for_numerical_entities(basic_stats_data)
    assert len(actual_result) == 1
    assert actual_result[0]['count'] == 1
    assert actual_result[0]['stderr'] is None
    assert actual_result[0]['count NaN'] == 4710
    assert len(actual_result[0]) == 10


def _get_parsed_data_numerical():
    basic_stats_data = BasicStatsNumericalDataRequest(
        measurements=['baseline', 'follow up1'],
        entities=['blood pressure', 'temperature'],
    )
    return basic_stats_data


def _get_parsed_data_categorical():
    basic_stats_data = BasicStatsNumericalDataRequest(
        measurements=['baseline', 'follow up1'],
        entities=['diabetes', 'biopsy'],
    )
    return basic_stats_data
