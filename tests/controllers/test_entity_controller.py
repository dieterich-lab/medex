from typing import List, Dict

import pytest
from flask import Flask

from medex.controller.entity import entity_controller
from medex.services.entity import EntityService


DEFAULT_ENTITIES = [
    {
        'key': 'cat1', 'type': 'String', 'description': None, 'categories': ['a', 'b'],
        'show': None, 'synonym': None, 'unit': None
    },
    {
        'key': 'num1', 'type': 'Double', 'unit': None,
        'description': None, 'categories': None, 'show': None, 'synonym': None
    },
]


class EntityServiceMock(EntityService):
    def __init__(self):  # noqa
        pass

    def get_all_as_dict(self) -> List[Dict[str, any]]:
        return DEFAULT_ENTITIES


@pytest.fixture
def helper_mock(mocker):
    mocker.patch(
        'medex.controller.entity.get_entity_service',  # noqa
        return_value=EntityServiceMock()
    )


@pytest.fixture
def test_client():
    app = Flask(__name__)
    app.register_blueprint(entity_controller)
    yield app.test_client()


def test_get_all(helper_mock, test_client):
    rv = test_client.get('/all')
    assert rv.status == '200 OK'
    assert rv.get_json() == DEFAULT_ENTITIES
