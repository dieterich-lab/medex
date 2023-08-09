import json

import pytest
from flask import Flask

from medex.controller.table_browser import filtered_data_controller
from tests.mocks.data_service import DataServiceMock


@pytest.fixture
def data_service_mock():
    yield DataServiceMock()


@pytest.fixture
def helper_mock(mocker):
    mocker.patch(
        'medex.controller.table_browser.get_data_service',  # noqa
        return_value=DataServiceMock()
    )


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(filtered_data_controller)
    yield app.test_client()


def test_get_filtered_flat_data(helper_mock, test_client):
    url = '/flat?columns%5B0%5D%5Bdata%5D=patient_id&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc&start=0&length' \
          '=10&table_data=%7B%22measurements%22%3A%5B%22baseline%22%2C%221%20year%20followup%22%5D%2C%22entities%22' \
          '%3A%5B%22basis_ahf%22%5D%7D'

    rv = test_client.get(url)
    rv_json = json.loads(rv.get_data(as_text=True))
    assert rv.status == '200 OK'
    assert rv_json['data'] == [
        {'patient_id': 'p1', 'measurement': 'baseline', 'key': 'cat1', 'value': 'ja'},
        {'patient_id': 'p2', 'measurement': 'baseline', 'key': 'num1', 'value': '120'},
    ]
    assert rv_json['iTotalDisplayRecords'] == 2
    assert rv_json['iTotalRecords'] == 2


def test_get_filtered_by_measurement_data(helper_mock, test_client):
    url = '/by_measurement?columns%5B0%5D%5Bdata%5D=patient_id&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=asc' \
          '&start=0&length=10&table_data=%7B%22measurements%22%3A%5B%22baseline%22%2C%221%20year%20followup%22%5D%2C' \
          '%22entities%22%3A%5B%22basis_ahf%22%5D%7D'

    rv = test_client.get(url)
    rv_json = rv.get_json()
    assert rv.status == '200 OK'
    assert rv_json['data'] == [
        {'patient_id': 'p1', 'measurement': 'baseline', 'cat1': 'ja', 'num1': '135', 'total': 3},
        {'patient_id': 'p2', 'measurement': 'baseline', 'cat1': 'nein', 'num1': '128', 'total': 3}
    ]
    assert rv_json['iTotalDisplayRecords'] == 3
    assert rv_json['iTotalRecords'] == 3
