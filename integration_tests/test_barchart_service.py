import pytest
from medex.dto.barchart import BarChartDataRequest, DateRange
from medex.services.barchart import BarChartService
from modules.models import TableCategorical, NameType
from tests.mocks.filter_service import FilterServiceMock
# noinspection PyUnresolvedReferences
from integration_tests.fixtures.db_session import db_session


@pytest.fixture
def setup_barchart_data(db_session):
    db_session.add_all([
        NameType(orders=1, key='diabetes', type='String'),
        NameType(orders=1, key='gender', type='String'),
        TableCategorical(
            name_id='p1', case_id='c1', measurement='baseline', date='2021-05-15', key='diabetes', value='nein'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='baseline', date='2021-06-28', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='follow up1', date='2022-06-28', key='diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p3', case_id='c3', measurement='baseline', date='2021-09-18', key='gender', value='female'
        ),
        TableCategorical(
            name_id='p3', case_id='c3', measurement='follow up1', date='2022-09-18', key='gender', value='female'
        ),
    ])
    db_session.commit()


@pytest.fixture
def filter_service_mock():
    yield FilterServiceMock()


def test_get_barchart_json(db_session, filter_service_mock, setup_barchart_data):
    service = BarChartService(db_session, filter_service_mock)
    barchart_data = _get_barchart_data()
    image_json = service.get_barchart_json(barchart_data)
    assert image_json.startswith('{"data"')


def test_get_barchart_svg(db_session, filter_service_mock, setup_barchart_data):
    service = BarChartService(db_session, filter_service_mock)
    barchart_data = _get_barchart_data()
    image_data = service.get_barchart_svg(barchart_data)
    byte_string = image_data.decode('utf-8')
    assert byte_string.find('<svg')


def _get_barchart_data():
    barchart_data = BarChartDataRequest(
        measurements=['baseline', 'follow up1'],
        key='diabetes',
        categories=['ja', 'nein'],
        plot_type='count',
        date_range=DateRange(from_date='2021-05-15', to_date='2022-09-18'),
    )
    return barchart_data
