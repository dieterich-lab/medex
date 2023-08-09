from io import StringIO

from sqlalchemy import select

from medex.database_schema import HeaderTable
from medex.services.importer.header import HeaderImporter

# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


def get_headers(db_session):
    return db_session.execute(select(HeaderTable.patient_id, HeaderTable.measurement)).first()


def test_default(db_session):
    importer = HeaderImporter(
        file_handle=None,
        source_name='/bla/import/header.csv',
        db_session=db_session
    )

    importer.setup_header_names()

    headers = get_headers(db_session)
    assert headers.patient_id == 'Patient_ID'
    assert headers.measurement == 'Measurement'


def test_simple(db_session):
    importer = HeaderImporter(
        file_handle=StringIO("foo,ignored,bar\n"),
        source_name='/bla/import/header.csv',
        db_session=db_session
    )

    importer.setup_header_names()

    headers = get_headers(db_session)
    assert headers.patient_id == 'foo'
    assert headers.measurement == 'bar'


def test_bad_headers(db_session, capsys):
    importer = HeaderImporter(
        file_handle=StringIO("bad\n"),
        source_name='/bla/import/header.csv',
        db_session=db_session
    )

    importer.setup_header_names()

    assert capsys.readouterr().out.startswith('WARNING')
    headers = get_headers(db_session)
    assert headers.patient_id == 'Patient_ID'
    assert headers.measurement == 'Measurement'
