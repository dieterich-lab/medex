from io import StringIO

from sqlalchemy import select

from modules.models import Header
from medex.services.importer.header import HeaderImporter

# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


def get_headers(db_session):
    return db_session.execute(select(Header.name_id, Header.measurement)).first()


def test_default(db_session):
    importer = HeaderImporter(
        file_handle=None,
        source_name='/bla/import/header.csv',
        db_session=db_session
    )

    importer.setup_header_names()

    headers = get_headers(db_session)
    assert headers.name_id == 'Name_ID'
    assert headers.measurement == 'measurement'


def test_simple(db_session):
    importer = HeaderImporter(
        file_handle=StringIO("foo,ignored,bar\n"),
        source_name='/bla/import/header.csv',
        db_session=db_session
    )

    importer.setup_header_names()

    headers = get_headers(db_session)
    assert headers.name_id == 'foo'
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
    assert headers.name_id == 'Name_ID'
    assert headers.measurement == 'measurement'
