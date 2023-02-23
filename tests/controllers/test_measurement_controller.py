import pytest
from flask import Flask

from medex.controller.measurement import measurement_controller
from medex.dto.measurement import MeasurementInfo
from medex.services.measurement import MeasurementService


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(measurement_controller)
    yield app.test_client()


class MeasurementServiceMock(MeasurementService):
    def __init__(self):  # noqa
        pass

    def get_info(self) -> MeasurementInfo:
        return MeasurementInfo(
            display_name='Visite',
            values=['Aufnahme', '1. Kontrolle', '2. Kontrolle']
        )


@pytest.fixture
def measurement_service(mocker):
    mocker.patch(
        'medex.controller.measurement.get_measurement_service',  # noqa
        return_value=MeasurementServiceMock()
    )
    yield


def test_it(test_client, measurement_service):
    rv = test_client.get('/')
    assert rv.status == '200 OK'
    assert rv.get_json() == {
        'display_name': 'Visite',
        'values': ['Aufnahme', '1. Kontrolle', '2. Kontrolle']
    }
