import pytest
from flask import Flask

from medex.controller.data import data_controller
from medex.dto.data import SingleDataItem, MeasurementDataItem
from tests.mocks.data_service import DataServiceMock


@pytest.fixture
def data_service_mock():
    yield DataServiceMock()


@pytest.fixture
def helper_mock(mocker):
    mocker.patch(
        'medex.controller.data.get_data_service',  # noqa
        return_value=DataServiceMock()
    )


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(data_controller)
    yield app.test_client()


def test_get_filtered_flat_data(helper_mock, test_client):
    rv = test_client.get(
        '/filtered_data_flat',
        json={
            'measurements': ['baseline'],
            'entities': ['cat1', 'num1'],
            'pagination_info': {'offset': 1, 'limit': 2},
            'sort_order': {'items': [{'column': 'name_id', 'direction': 'desc'}]}
        }
    )
    assert rv.status == '200 OK'
    assert rv.get_json() == [
        SingleDataItem(name_id='p1', measurement='baseline', key='cat1', value='ja'),
        SingleDataItem(name_id='p2', measurement='baseline', key='num1', value=120)
    ]


def test_get_filtered_by_measurement_data(helper_mock, test_client):
    rv = test_client.get(
        '/filtered_data_by_measurement',
        json={
            'measurements': ['baseline'],
            'entities': ['cat1', 'num1'],
            'pagination_info': {'offset': 1, 'limit': 2},
            'sort_order': {'items': [{'column': 'name_id', 'direction': 'desc'}]}
        }
    )
    assert rv.status == '200 OK'
    assert rv.get_json() == [
        MeasurementDataItem(name_id='p1', measurement='baseline', data_by_entity_id={'cat1': 'ja', 'num1': 135}),
        MeasurementDataItem(name_id='p2', measurement='baseline', data_by_entity_id={'cat1': 'nein', 'num1': 128})
    ]
