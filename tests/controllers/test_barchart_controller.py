from urllib.parse import urlencode
import pytest
from flask import Flask
from medex.controller.barchart import barchart_controller
from tests.mocks.barchart_service import BarChartServiceMock


@pytest.fixture
def helper_mock(mocker):
    mocker.patch(
        'medex.controller.barchart.get_barchart_service',  # noqa
        return_value=BarChartServiceMock()
    )


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(barchart_controller)
    yield app.test_client()


def test_get_barchart_json(helper_mock, test_client):
    query_parameter_string = _get_query_parameter_string()
    url = '/barchart/json?' + query_parameter_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def test_get_barchart_svg_download(test_client, helper_mock):
    query_parameter_string = _get_query_parameter_string()
    url = '/barchart/download?' + query_parameter_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def _get_query_parameter_string():
    request_dict = {
        'barchart_data': {
            'measurements': ['baseline', 'follow up1'],
            'key': 'diabetes',
            'categories': ['ja', 'nein'],
            'plot_type': '%'
        }
    }
    query_string = urlencode(request_dict)
    return query_string
