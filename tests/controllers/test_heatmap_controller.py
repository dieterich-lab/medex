from urllib.parse import urlencode

import pytest
from flask import Flask

from medex.controller.heatmap import heatmap_controller
from tests.mocks.heatmap_service import HeatmapServiceMock


@pytest.fixture
def helper_mock(mocker):
    mocker.patch(
        'medex.controller.heatmap.get_heatmap_service',
        return_value=HeatmapServiceMock()
    )


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(heatmap_controller)
    return app.test_client()


def test_get_heatmap_plot_json(test_client, helper_mock):
    query_parameter_string = _get_parameter_string()
    url = '/json?' + query_parameter_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def test_get_heatmap_svg_for_download(test_client, helper_mock):
    query_parameter_string = _get_parameter_string()
    url = '/download?' + query_parameter_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def _get_parameter_string():
    request_data = {
        'heatmap_data': {
            'entities': ['blood_pressure', 'temperature'],
        }
    }
    query_parameter_string = urlencode(request_data)
    return query_parameter_string
