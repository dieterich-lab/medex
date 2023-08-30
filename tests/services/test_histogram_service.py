from datetime import datetime

import pytest

from medex.dto.histogram import HistogramDataRequest
from medex.services.histogram import HistogramService
from medex.database_schema import NumericalValueTable, CategoricalValueTable
from tests.mocks.filter_service import FilterServiceMock
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


@pytest.fixture
def setup_histogram_data(db_session):
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
        CategoricalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2021, 5, 15),
            key='diabetes', value='nein'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2021, 6, 28),
            key='diabetes', value='ja'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='follow up1', date_time=datetime(2022, 6, 28),
            key='diabetes', value='ja'
        )
    ])
    db_session.commit()


@pytest.fixture
def filter_service_mock():
    yield FilterServiceMock()


def test_get_histogram_json(db_session, filter_service_mock, setup_histogram_data):
    service = HistogramService(db_session, filter_service_mock)
    histogram_data = _get_parsed_data()
    image_json = service.get_image_json(histogram_data)
    assert image_json.startswith('{"data"')


def test_get_histogram_svg(db_session, filter_service_mock, setup_histogram_data):
    service = HistogramService(db_session, filter_service_mock)
    histogram_data = _get_parsed_data()
    image_data = service.get_image_svg(histogram_data)
    byte_string = image_data.decode('utf-8')
    assert byte_string.find('<svg')


def _get_parsed_data():
    histogram_data = HistogramDataRequest(
        measurements=['baseline', 'follow up1'],
        numerical_entity='blood pressure',
        categorical_entity='diabetes',
        categories=['ja', 'nein'],
        bins=25,
    )
    return histogram_data
