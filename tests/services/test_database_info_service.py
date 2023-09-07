from datetime import datetime
from medex.dto.entity import EntityType
from medex.services.database_info import DatabaseInfoService
from medex.database_schema import EntityTable, CategoricalValueTable, NumericalValueTable, PatientTable, DateValueTable
# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


def test_empty_database(db_session):
    service = DatabaseInfoService(db_session)
    result = service.get()
    assert result.number_of_patients == 0
    assert result.number_of_numerical_entities == 0
    assert result.number_of_categorical_entities == 0
    assert result.number_of_date_entities == 0
    assert result.number_of_numerical_data_items == 0
    assert result.number_of_categorical_data_items == 0
    assert result.number_of_date_data_items == 0


def test_simple_database(db_session):
    db_session.add_all([
        PatientTable(patient_id='nn', case_id='1'),
        EntityTable(key='n1', type=str(EntityType.NUMERICAL.value)),
        EntityTable(key='n2', type=str(EntityType.NUMERICAL.value)),
        EntityTable(key='c1', type=str(EntityType.CATEGORICAL.value)),
        EntityTable(key='c2', type=str(EntityType.CATEGORICAL.value)),
        EntityTable(key='c3', type=str(EntityType.CATEGORICAL.value)),
        EntityTable(key='d1', type=str(EntityType.DATE.value)),
        NumericalValueTable(key='n1', value=1.1),
        NumericalValueTable(key='n1', value=2.1),
        NumericalValueTable(key='n1', value=3.1),
        CategoricalValueTable(key='c1', value='x'),
        CategoricalValueTable(key='c1', value='x'),
        DateValueTable(key='d1', value=datetime(year=1970, month=1, day=1)),
    ])
    service = DatabaseInfoService(db_session)
    result = service.get()
    assert result.number_of_patients == 1
    assert result.number_of_numerical_entities == 2
    assert result.number_of_categorical_entities == 3
    assert result.number_of_date_entities == 1
    assert result.number_of_numerical_data_items == 3
    assert result.number_of_categorical_data_items == 2
    assert result.number_of_date_data_items == 1


def test_multiple_case_ids(db_session):
    db_session.add_all([
        PatientTable(patient_id='nn', case_id='1'),
        PatientTable(patient_id='nn', case_id='2'),
        EntityTable(key='n1', type=str(EntityType.NUMERICAL.value)),
        NumericalValueTable(key='n1', case_id='1', value=1.1),
        NumericalValueTable(key='n1', case_id='2', value=2.1),
    ])
    service = DatabaseInfoService(db_session)
    result = service.get()
    assert result.number_of_patients == 1
    assert result.number_of_numerical_entities == 1
    assert result.number_of_categorical_entities == 0
    assert result.number_of_date_entities == 0
    assert result.number_of_numerical_data_items == 2
    assert result.number_of_categorical_data_items == 0
    assert result.number_of_date_data_items == 0
