import pytest

from medex.database_schema import NameType, TableCategorical, TableNumerical
from medex.dto.entity import EntityType, Entity
from medex.services.entity import EntityService
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


@pytest.fixture
def setup_entities(db_session):
    db_session.add_all([
        NameType(key='Diabetes', type=str(EntityType.CATEGORICAL.value), description='Diabetes ja/nein'),
        NameType(key='Blutdruck', type=str(EntityType.NUMERICAL.value), unit='mmHg'),
        TableCategorical(
            name_id='p1', case_id='c1', measurement='baseline', date='2022-03-17', key='Diabetes', value='ja'
        ),
        TableCategorical(
            name_id='p2', case_id='c2', measurement='baseline', date='2022-03-17', key='Diabetes', value='nein'
        ),
        TableNumerical(
            name_id='p1', case_id='c1', measurement='baseline', date='2022-03-17', key='Blutdruck', value=123
        ),
        TableNumerical(
            name_id='p2', case_id='c2', measurement='baseline', date='2022-03-17', key='Blutdruck', value=145
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
