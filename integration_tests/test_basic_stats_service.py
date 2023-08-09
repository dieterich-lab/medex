import pytest
from medex.dto.basic_stats import BasicStatsNumericalDataRequest
from medex.services.basic_stats import BasicStatisticsService
from medex.database_schema import TableNumerical, NameType, Patient, TableCategorical
from tests.mocks.filter_service import FilterServiceMock
# noinspection PyUnresolvedReferences
from integration_tests.fixtures.db_session import db_session


@pytest.fixture
def setup_basic_stats_data_minimal(db_session):
    db_session.add_all([
        Patient(name_id='p1', case_id='c1'),
        NameType(key='blood pressure', type='Double'),
        TableNumerical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15',
            key='blood pressure', value=129
        ),
    ])
    db_session.commit()


@pytest.fixture
def setup_basic_stats_data(db_session):
    db_session.add_all([
        Patient(name_id='p1', case_id='c1'),
        Patient(name_id='p2', case_id='c2'),
        Patient(name_id='p3', case_id='c3'),
        NameType(key='blood pressure', type='Double'),
        NameType(key='temperature', type='Double'),
        NameType(key='diabetes', type='String'),
        NameType(key='biopsy', type='String'),
        TableNumerical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='blood pressure', value=129
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-05-15', key='blood pressure', value=138
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-05-15', key='blood pressure', value=135
        ),
        TableNumerical(
            name_id='p3', case_id='c3', measurement='baseline', date='2021-09-27', key='temperature', value=38.5
        ),
        TableNumerical(
            name_id='p3', case_id='c3', measurement='follow up1', date='2022-09-27', key='temperature', value=41.5
        ),
        TableCategorical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='diabetes', value='nein'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-07-21', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-05-15', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p3', case_id='c3', measurement='baseline', date='2022-03-09', key='biopsy', value='ja'
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
