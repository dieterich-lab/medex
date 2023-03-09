from typing import List, Dict

import pytest
from flask import Flask

from medex.controller.database_info import database_info_controller
from medex.dto.database_info import DatabaseInfo
from medex.services.database_info import DatabaseInfoService


class DatabaseInfoServiceMock(DatabaseInfoService):
    def __init__(self):  # noqa
        pass

    def get(self):
        return DatabaseInfo(
            number_of_patients=1,
            number_of_numerical_entities=2,
            number_of_categorical_entities=3,
            number_of_date_entities=4,
            number_of_numerical_data_items=5,
            number_of_categorical_data_items=6,
            number_of_date_data_items=7
        )


@pytest.fixture
def helper_mock(mocker):
    mocker.patch(
        'medex.controller.database_info.get_database_info_service',  # noqa
        return_value=DatabaseInfoServiceMock()
    )


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(database_info_controller)
    yield app.test_client()


DB_INFO = {
    'number_of_patients': 1,
    'number_of_numerical_entities': 2,
    'number_of_categorical_entities': 3,
    'number_of_date_entities': 4,
    'number_of_numerical_data_items': 5,
    'number_of_categorical_data_items': 6,
    'number_of_date_data_items': 7,
}


def test_get(helper_mock, test_client):
    rv = test_client.get('/')
    assert rv.status == '200 OK'
    assert rv.get_json() == DB_INFO
