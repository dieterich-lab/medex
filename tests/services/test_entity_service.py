from datetime import datetime

import pytest

from medex.database_schema import EntityTable, CategoricalValueTable, NumericalValueTable
from medex.dto.entity import EntityType, Entity
from medex.services.entity import EntityService
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


@pytest.fixture
def setup_entities(db_session):
    db_session.add_all([
        EntityTable(key='Diabetes', type=str(EntityType.CATEGORICAL.value), description='Diabetes ja/nein'),
        EntityTable(key='Blutdruck', type=str(EntityType.NUMERICAL.value), unit='mmHg'),
        CategoricalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2022, 3, 17),
            key='Diabetes', value='ja'
        ),
        CategoricalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2022, 3, 17),
            key='Diabetes', value='nein'
        ),
        NumericalValueTable(
            patient_id='p1', case_id='c1', measurement='baseline', date_time=datetime(2022, 3, 17),
            key='Blutdruck', value=123
        ),
        NumericalValueTable(
            patient_id='p2', case_id='c2', measurement='baseline', date_time=datetime(2022, 3, 17),
            key='Blutdruck', value=145
        )
    ])


def test_get_all(db_session, setup_entities):
    service = EntityService(db_session)
    assert service.get_all() == [
        Entity(key='Blutdruck', type=EntityType.NUMERICAL, unit='mmHg', min=123, max=145),
        Entity(key='Diabetes', type=EntityType.CATEGORICAL, description='Diabetes ja/nein', categories=['ja', 'nein'])
    ]


def test_get_all_as_dict(db_session, setup_entities):
    service = EntityService(db_session)
    assert service.get_all_as_dict() == [
        {
            'key': 'Blutdruck', 'type': 'Double', 'unit': 'mmHg', 'min': 123.0, 'max': 145.0,
            'description': None, 'categories': None, 'show': None, 'synonym': None
        },
        {
            'key': 'Diabetes', 'type': 'String', 'description': 'Diabetes ja/nein', 'categories': ['ja', 'nein'],
            'show': None, 'synonym': None, 'unit': None, 'min': None, 'max': None,
        },
    ]
