import pytest

from medex.dto.histogram import HistogramDataRequest, DateRange
from medex.services.histogram import HistogramService
from modules.models import TableNumerical, TableCategorical
from tests.mocks.filter_service import FilterServiceMock
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


@pytest.fixture
def setup_data(db_session):
    db_session.add_all([
        TableNumerical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='blood pressure', value=129
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-05-15', key='blood pressure', value=138
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-05-15', key='blood pressure', value=135
        ),
        TableCategorical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='diabetes', value='nein'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-06-28', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-06-28', key='diabetes', value='ja'
        )
    ])
    db_session.commit()


@pytest.fixture
def filter_service_mock():
    yield FilterServiceMock()


def test_get_histogram_json(db_session, filter_service_mock, setup_data):
    service = HistogramService(db_session, filter_service_mock)
    histogram_data = _get_parsed_data()
    image_json = service.get_image_json(histogram_data)
    assert image_json.startswith('{"data"')


def test_get_histogram_svg(db_session, filter_service_mock, setup_data):
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
        date_range=DateRange(from_date='2021-05-15', to_date='2022-06-28'),
    )
    return histogram_data
