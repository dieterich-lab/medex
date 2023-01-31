from urllib.parse import urlencode

import pytest
from flask import Flask

from medex.controller.boxplot import boxplot_controller
from tests.mocks.boxplot_service import BoxplotServiceMock


@pytest.fixture
def helper_mock(mocker):
    mocker.patch(
        'medex.controller.boxplot.get_boxplot_service',  # noqa
        return_value=BoxplotServiceMock()
    )


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(boxplot_controller)
    yield app.test_client()


def test_get_json(test_client, helper_mock):
    query_parameter_string = _get_parameter_string()
    url = '/boxplot/json?' + query_parameter_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def test_get_svg_for_download(test_client, helper_mock):
    query_parameter_string = _get_parameter_string()
    url = '/boxplot/download?' + query_parameter_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def _get_parameter_string():
    request_dict = {
        'boxplot_data': {
            'measurements': ['baseline', 'follow up1'],
            'numerical_entity': 'blood pressure',
            'categorical_entity': 'diabetes',
            'categories': ['ja', 'nein'],
            'plot_type': 'linear',
        }
    }
    query_parameter_string = urlencode(request_dict)
    return query_parameter_string
