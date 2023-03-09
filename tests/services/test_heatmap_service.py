import json
import pytest
from medex.dto.heatmap import HeatmapDataRequest
from medex.services.heatmap import HeatmapService
from medex.database_schema import TableNumerical
from tests.mocks.filter_service import FilterServiceMock
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


@pytest.fixture
def setup_heatmap_data(db_session):
    db_session.add_all([
        TableNumerical(name_id='p1', key='blood_pressure', value=135, date='2021-06-20'),
        TableNumerical(name_id='p2', key='blood_pressure', value=139, date='2021-07-14'),
        TableNumerical(name_id='p3', key='blood_pressure', value=128, date='2021-08-05'),
        TableNumerical(name_id='p1', key='temperature', value=35, date='2021-05-15'),
        TableNumerical(name_id='p2', key='temperature', value=38, date='2021-07-14'),
        TableNumerical(name_id='p3', key='echo_lvef', value=55, date='2022-03-21'),
        TableNumerical(name_id='p4', key='echo_lvef', value=80, date='2022-10-05')
    ])
    db_session.commit()


@pytest.fixture
def filter_service_mock():
    yield FilterServiceMock()


def test_get_heatmap_json(db_session, filter_service_mock, setup_heatmap_data):
    service = HeatmapService(db_session, filter_service_mock)
    heatmap_data = _get_parsed_data()
    image_json = service.get_heatmap_json(heatmap_data)
    assert image_json.startswith('{"data"')
    assert json.loads(image_json)


def test_get_heatmap_svg(db_session, filter_service_mock, setup_heatmap_data):
    service = HeatmapService(db_session, filter_service_mock)
    heatmap_data = _get_parsed_data()
    image_data = service.get_heatmap_svg(heatmap_data)
    byte_string = image_data.decode('utf-8')
    assert byte_string.find('<svg')


def _get_parsed_data():
    heatmap_data = HeatmapDataRequest(
        entities=['blood_pressure', 'temperature', 'echo_lvef'],
    )
    return heatmap_data
