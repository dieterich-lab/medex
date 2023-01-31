import json

import pytest

from medex.dto.boxplot import BoxplotDataRequest, DateRange
from medex.services.boxplot import BoxplotService
from medex.services.histogram import HistogramService
from tests.mocks.filter_service import FilterServiceMock
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session
# noinspection PyUnresolvedReferences
from tests.services.test_histogram_service import setup_histogram_data


@pytest.fixture
def filter_service_mock():
    yield FilterServiceMock()


def test_get_boxplot_json(db_session, filter_service_mock, setup_histogram_data):
    histogram_service = HistogramService(db_session, filter_service_mock)
    service = BoxplotService(db_session, filter_service_mock, histogram_service)
    boxplot_data = _get_parsed_data()
    merged_json = service.get_boxplot_json(boxplot_data)
    assert merged_json.startswith('{"image_json": {"data": ')
    assert merged_json.find("table")
    assert json.loads(merged_json)


def test_get_boxplot_svg(db_session, filter_service_mock, setup_histogram_data):
    histogram_service = HistogramService(db_session, filter_service_mock)
    service = BoxplotService(db_session, filter_service_mock, histogram_service)
    boxplot_data = _get_parsed_data()
    image_data = service.get_boxplot_svg(boxplot_data)
    byte_string = image_data.decode('utf-8')
    assert byte_string.find('<svg')


def _get_parsed_data():
    boxplot_data = BoxplotDataRequest(
        measurements=['baseline', 'follow up1'],
        numerical_entity='blood pressure',
        categorical_entity='diabetes',
        categories=['ja', 'nein'],
        plot_type='linear',
        date_range=DateRange(from_date='2021-05-15', to_date='2022-06-28'),
    )
    return boxplot_data
