from urllib.parse import urlencode

import pytest
from flask import Flask

from medex.controller.basic_stats import basic_stats_controller
from tests.mocks.basic_stats_service import BasicStatisticsServiceMock


@pytest.fixture
def helper_mock(mocker):
    mocker.patch(
        'medex.controller.basic_stats.get_basic_stats_service',  # noqa
        return_value=BasicStatisticsServiceMock()
    )


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(basic_stats_controller)
    yield app.test_client()


def test_get_basic_stats_numerical(test_client, helper_mock):
    parameter_string = _get_parameter_string_numerical()
    url = '/numerical?' + parameter_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def test_get_basic_stats_categorical(test_client, helper_mock):
    parameter_string = _get_parameter_string_categorical()
    url = '/categorical?' + parameter_string
    url = url.replace('%27', '%22')
    rv = test_client.get(url)
    assert rv.status == '200 OK'


def _get_parameter_string_numerical():
    request_data = {
        'basic_stats_data': {
            'measurements': ['baseline'],
            'entities': ['blood pressure'],
        }
    }
    query_parameter_string = urlencode(request_data)
    return query_parameter_string


def _get_parameter_string_categorical():
    request_data = {
        'basic_stats_data': {
            'measurements': ['baseline', 'follow up1'],
            'entities': ['diabetes', 'biopsy'],
        }
    }
    query_parameter_string = urlencode(request_data)
    return query_parameter_string
