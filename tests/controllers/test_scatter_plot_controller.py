from urllib.parse import urlencode
import pytest
from flask import Flask
from medex.controller.scatter_plot import scatter_plot_controller
from tests.mocks.scatter_plot_service import ScatterPlotServiceMock


@pytest.fixture
def helper_mock(mocker):
    mocker.patch(
        'medex.controller.scatter_plot.get_scatter_plot_service',  # noqa
        return_value=ScatterPlotServiceMock()
    )


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(scatter_plot_controller)
    yield app.test_client()


def test_get_image_json(test_client, helper_mock):
    request_dict = {
        'scatter_plot_data': {
            'measurement_x_axis': 'baseline',
            'entity_x_axis': 'blood_pressure',
            'measurement_y_axis': 'baseline',
            'entity_y_axis': 'temperature',
        }
    }
    query_string = urlencode(request_dict)
    url = '/scatter_plot/json?' + query_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def test_get_svg_download(test_client, helper_mock):
    request_dict = {
        'scatter_plot_data': {
            'measurement_x_axis': 'baseline',
            'entity_x_axis': 'blood_pressure',
            'measurement_y_axis': 'baseline',
            'entity_y_axis': 'temperature',
        }
    }
    query_string = urlencode(request_dict)
    url = '/scatter_plot/download?' + query_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'
