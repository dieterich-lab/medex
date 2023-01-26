from urllib.parse import urlencode

import pytest
from flask import Flask

from medex.controller.histogram import histogram_controller
from tests.mocks.histogram_service import HistogramServiceMock


@pytest.fixture
def helper_mock(mocker):
    mocker.patch(
        'medex.controller.histogram.get_histogram_service',  # noqa
        return_value=HistogramServiceMock()
    )


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(histogram_controller)
    yield app.test_client()


def test_get_histogram_json(test_client, helper_mock):
    query_parameter_string = _get_query_parameter_string()
    url = '/histogram/json?' + query_parameter_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def test_get_histogram_svg_download(test_client, helper_mock):
    query_parameter_string = _get_query_parameter_string()
    url = '/histogram/download?' + query_parameter_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def _get_query_parameter_string():
    request_dict = {
        'histogram_data': {
            'measurements': ['baseline', 'follow up1'],
            'numerical_entity': 'blood pressure',
            'categorical_entity': 'diabetes',
            'categories': ['ja', 'nein'],
        }
    }
    query_parameter_string = urlencode(request_dict)
    return query_parameter_string
