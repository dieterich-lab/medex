import pytest

from medex.database_schema import SessionTable, SessionPatientsMatchingFilterTable, SessionFilteredPatientTable
from medex.services.session import SessionService

# noinspection PyUnresolvedReferences
from tests.fixtures.db_session import db_session


def setup_session(db_session, service: SessionService):
    service.touch()
    db_session.add_all([
        SessionPatientsMatchingFilterTable(session_id=service.get_id(), patient_id='p1', filter='f1'),
        SessionFilteredPatientTable(session_id=service.get_id(), patient_id='p1'),
    ])
    db_session.commit()


def test_expire_old_sessions_on_fresh_db(db_session):
    SessionService.expire_old_sessions(db_session)


@pytest.mark.freeze_time
def test_expire_old_sessions_on_fresh_session(db_session, freezer):
    freezer.move_to('2017-05-20 11:03:00')
    old_session = SessionService(session_id='old-session', database_session=db_session)
    setup_session(db_session, old_session)
    fresh_session = SessionService(session_id='fresh-session', database_session=db_session)
    setup_session(db_session, fresh_session)
    freezer.move_to('2017-05-20 15:17:15')
    fresh_session.touch()
    freezer.move_to('2017-05-20 19:03:01')

    SessionService.expire_old_sessions(db_session)

    assert db_session.get(SessionTable, 'old-session') is None
    assert len(
        db_session.query(SessionPatientsMatchingFilterTable)
        .where(SessionPatientsMatchingFilterTable.session_id == 'old-session')
        .all()
    ) == 0
    assert len(
        db_session.query(SessionFilteredPatientTable)
        .where(SessionFilteredPatientTable.session_id == 'old-session')
        .all()
    ) == 0

    assert db_session.get(SessionTable, 'fresh-session') is not None
    assert len(
        db_session.query(SessionPatientsMatchingFilterTable)
        .where(SessionPatientsMatchingFilterTable.session_id == 'fresh-session')
        .all()
    ) == 1
    assert len(
        db_session.query(SessionFilteredPatientTable)
        .where(SessionFilteredPatientTable.session_id == 'fresh-session')
        .all()
    ) == 1
