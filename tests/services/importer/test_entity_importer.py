from io import StringIO

import pytest
from sqlalchemy import select

from medex.services.importer.entitity import EntityImporter
from medex.services.importer.generic_importer import HeaderLineMissing, BadHeaderLine
from medex.database_schema import EntityTable

# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


def test_empty_file(db_session):
    importer = EntityImporter(
        file_handle=StringIO(''),
        source_name='/bla/import/entities.csv',
        db_session=db_session
    )
    with pytest.raises(HeaderLineMissing):
        importer.import_all()


MISSING_COLUMN_ENTITY_CSV = """key
some_num_entity
"""


def test_missing_column(db_session):
    importer = EntityImporter(
        file_handle=StringIO(MISSING_COLUMN_ENTITY_CSV),
        source_name='/bla/import/entities.csv',
        db_session=db_session
    )
    with pytest.raises(BadHeaderLine):
        importer.import_all()


MINIMAL_ENTITY_CSV = """key,type
some_num_entity,Double
"""


def test_minimal_import(db_session):
    importer = EntityImporter(
        file_handle=StringIO(MINIMAL_ENTITY_CSV),
        source_name='/bla/import/entities.csv',
        db_session=db_session
    )

    importer.import_all()

    result = db_session.execute(select(EntityTable.key, EntityTable.type)).all()
    assert len(result) == 1
    assert result[0].key == 'some_num_entity'
    assert result[0].type == 'Double'


ALL_FIELDS_IMPORT = """synonym,key,unit,type,description
my_synonym,some_cat_entity,bogus unit,String,Dät könnt auch Dütßch sein
"""


def test_all_fields_import(db_session):
    importer = EntityImporter(
        file_handle=StringIO(ALL_FIELDS_IMPORT),
        source_name='/bla/import/entities.csv',
        db_session=db_session
    )

    importer.import_all()

    result = db_session.execute(select(
        EntityTable.key, EntityTable.type, EntityTable.synonym, EntityTable.unit, EntityTable.description
    )).all()
    assert len(result) == 1
    assert result[0].key == 'some_cat_entity'
    assert result[0].type == 'String'
    assert result[0].synonym == 'my_synonym'
    assert result[0].unit == 'bogus unit'
    assert result[0].description == 'Dät könnt auch Dütßch sein'


UNKNOWN_COLUMN_ENTITY_CSV = """key,type,bogus
some_num_entity,Double,bla blub
"""


def test_unknown_column_import(db_session, capsys):
    importer = EntityImporter(
        file_handle=StringIO(UNKNOWN_COLUMN_ENTITY_CSV),
        source_name='/bla/import/entities.csv',
        db_session=db_session
    )

    importer.import_all()

    result = db_session.execute(select(EntityTable.key, EntityTable.type)).all()
    assert len(result) == 1
    assert result[0].key == 'some_num_entity'
    assert result[0].type == 'Double'
    assert capsys.readouterr().out == \
           "Warning: Header of /bla/import/entities.csv does contain unknown column 'bogus' - will be ignored.\n"


def test_large_import(db_session):
    data = "key,type\n" + "\n".join([
        f"some cat entity {i:03d},String"
        for i in range(150)
    ])
    importer = EntityImporter(
        file_handle=StringIO(data),
        source_name='/bla/import/entities.csv',
        db_session=db_session
    )

    importer.import_all()

    result = db_session.execute(select(EntityTable.key, EntityTable.type).order_by(EntityTable.key)).all()
    assert len(result) == 150
    for i in range(150):
        assert result[i].key == f"some cat entity {i:03d}"
        assert result[i].type == 'String'


EMPTY_LINE_ENTITY_CSV = """key,type

some_num_entity,Double



"""


def test_empty_line_import(db_session, capsys):
    importer = EntityImporter(
        file_handle=StringIO(EMPTY_LINE_ENTITY_CSV),
        source_name='/bla/import/entities.csv',
        db_session=db_session
    )

    importer.import_all()

    result = db_session.execute(select(EntityTable.key, EntityTable.type)).all()
    assert len(result) == 1
    assert result[0].key == 'some_num_entity'
    assert result[0].type == 'Double'
    assert capsys.readouterr().out == ''
