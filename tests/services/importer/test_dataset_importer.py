import datetime
from decimal import Decimal
from io import StringIO

import pytest
from sqlalchemy import select, insert

from medex.dto.entity import Entity
from medex.services.importer.dataset import DatasetImporter
from medex.services.importer.generic_importer import HeaderLineMissing, BadHeaderLine
from medex.database_schema import NameType, TableCategorical, TableNumerical, TableDate

# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


DEFAULT_ENTITIES_AS_DICTS = [
    {'key': 'Blutdruck', 'type': 'Double'},
    {'key': 'Diabetes', 'type': 'String'},
    {'key': 'Geburtsdatum', 'type': 'Date'}
]

DEFAULT_ENTITIES = [
    Entity(**x)
    for x in DEFAULT_ENTITIES_AS_DICTS
]


class EntityServiceMock:
    def get_all(self):  # noqa
        return DEFAULT_ENTITIES

    def refresh(self):
        pass


@pytest.fixture
def entity_service(db_session):
    db_session.execute(
        insert(NameType),
        DEFAULT_ENTITIES_AS_DICTS
    )
    yield EntityServiceMock()


def test_empty_file(db_session, entity_service):
    importer = DatasetImporter(
        file_handle=StringIO(''),
        source_name='/bla/import/dataset.csv',
        entity_service=entity_service,
        db_session=db_session
    )
    with pytest.raises(HeaderLineMissing):
        importer.import_all()


MISSING_COLUMN_ENTITY_CSV = """name_id,key
some_patient,Diabetes
"""


def test_missing_column(db_session, entity_service):
    importer = DatasetImporter(
        file_handle=StringIO(MISSING_COLUMN_ENTITY_CSV),
        source_name='/bla/import/dataset.csv',
        entity_service=entity_service,
        db_session=db_session
    )
    with pytest.raises(BadHeaderLine):
        importer.import_all()


MINIMAL_DATASET_CSV = """name_id,key,value
some_patient,Diabetes,Type II
"""


def test_minimal_import(db_session, entity_service):
    importer = DatasetImporter(
        file_handle=StringIO(MINIMAL_DATASET_CSV),
        source_name='/bla/import/dataset.csv',
        entity_service=entity_service,
        db_session=db_session
    )

    importer.import_all()

    result = db_session.execute(select(
        TableCategorical.name_id, TableCategorical.key, TableCategorical.value, TableCategorical.measurement
    )).all()
    assert len(result) == 1
    assert result[0].name_id == 'some_patient'
    assert result[0].key == 'Diabetes'
    assert result[0].value == 'Type II'
    assert result[0].measurement == '1'


ALL_FIELDS_IMPORT = """name_id,case_id,measurement,date,time,key,value
patientA,case1,baseline,2022-10-12,12:00:17,Diabetes,Type I
patientB,case2,follow up 1y,2022-10-13,12:00:18,Blutdruck,127.6
patientC,case3,follow up 2y,2022-10-14,12:00:19,Geburtsdatum,1928-03-18
"""


def test_all_fields_import(db_session, entity_service):
    importer = DatasetImporter(
        file_handle=StringIO(ALL_FIELDS_IMPORT),
        source_name='/bla/import/dataset.csv',
        entity_service=entity_service,
        db_session=db_session
    )

    importer.import_all()

    result_cat = db_session.execute(select(
        TableCategorical.name_id, TableCategorical.case_id, TableCategorical.measurement,
        TableCategorical.date, TableCategorical.time, TableCategorical.key,
        TableCategorical.value
    )).all()
    assert len(result_cat) == 1
    assert result_cat[0].name_id == 'patientA'
    assert result_cat[0].case_id == 'case1'
    assert result_cat[0].measurement == 'baseline'
    assert result_cat[0].date == '2022-10-12'
    assert result_cat[0].time == '12:00:17'
    assert result_cat[0].key == 'Diabetes'
    assert result_cat[0].value == 'Type I'

    result_num = db_session.execute(select(
        TableNumerical.name_id, TableNumerical.case_id, TableNumerical.measurement,
        TableNumerical.date, TableNumerical.time, TableNumerical.key,
        TableNumerical.value
    )).all()
    assert len(result_num) == 1
    assert result_num[0].name_id == 'patientB'
    assert result_num[0].case_id == 'case2'
    assert result_num[0].measurement == 'follow up 1y'
    assert result_num[0].date == '2022-10-13'
    assert result_num[0].time == '12:00:18'
    assert result_num[0].key == 'Blutdruck'
    assert float(result_num[0].value) == 127.6
    
    result_dat = db_session.execute(select(
        TableDate.name_id, TableDate.case_id, TableDate.measurement,
        TableDate.date, TableDate.time, TableDate.key,
        TableDate.value
    )).all()
    assert len(result_dat) == 1
    assert result_dat[0].name_id == 'patientC'
    assert result_dat[0].case_id == 'case3'
    assert result_dat[0].measurement == 'follow up 2y'
    assert result_dat[0].date == '2022-10-14'
    assert result_dat[0].time == '12:00:19'
    assert result_dat[0].key == 'Geburtsdatum'
    assert result_dat[0].value == datetime.date(year=1928, month=3, day=18)


def test_large_import(db_session, entity_service):
    data = "name_id,key,value\n" + "\n".join([
        "\n".join([
            f"patient{i:03d}a,Diabetes,Type {i}",
            f"patient{i:03d}b,Blutdruck,{120.0+i/3}",
            f"patient{i:03d}c,Geburtsdatum,{1870+i}-01-01",
        ])
        for i in range(150)
    ])
    importer = DatasetImporter(
        file_handle=StringIO(data),
        source_name='/bla/import/dataset.csv',
        entity_service=entity_service,
        db_session=db_session
    )

    importer.import_all()

    result_cat = db_session.execute(select(
        TableCategorical.name_id, TableCategorical.key, TableCategorical.value
    ).order_by(TableCategorical.name_id)).all()
    result_num = db_session.execute(select(
        TableNumerical.name_id, TableNumerical.key, TableNumerical.value
    ).order_by(TableNumerical.name_id)).all()
    result_dat = db_session.execute(select(
        TableDate.name_id, TableDate.key, TableDate.value
    ).order_by(TableDate.name_id)).all()

    assert len(result_cat) == 150
    assert len(result_num) == 150
    assert len(result_dat) == 150
    for i in range(150):
        assert result_cat[i].name_id == f"patient{i:03d}a"
        assert result_cat[i].key == 'Diabetes'
        assert result_cat[i].value == f"Type {i}"

        assert result_num[i].name_id == f"patient{i:03d}b"
        assert result_num[i].key == 'Blutdruck'
        assert round(result_num[i].value, 5) == round(Decimal(120.0 + i / 3.0), 5)

        assert result_dat[i].name_id == f"patient{i:03d}c"
        assert result_dat[i].key == 'Geburtsdatum'
        assert result_dat[i].value == datetime.date(year=1870+i, month=1, day=1)
