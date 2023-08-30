from sqlalchemy import delete

from medex.database_schema import SessionTable, SessionFilteredPatientTable, SessionPatientsMatchingFilterTable, SessionFilteredCaseIdTable
from datetime import datetime, timedelta


class SessionService:
    EXPIRATION_TIME = timedelta(hours=8)
    TOUCH_GRACE_PERIOD = timedelta(seconds=3)

    def __init__(self, database_session, session_id: str):
        self._database_session = database_session
        self._session_id = session_id
        self._last_touched = None

    def touch(self):
        now = datetime.now()
        if self._last_touched is not None and now < self._last_touched + self.TOUCH_GRACE_PERIOD:
            return
        db = self._database_session
        session = db.get(SessionTable, self._session_id)
        if session is None:
            session = SessionTable(
                id=self._session_id,
                created=now,
                last_touched=now
            )
            db.add(session)
        else:
            session.last_touched = now
        db.commit()
        self._last_touched = now

    def get_id(self):
        return self._session_id

    @classmethod
    def expire_old_sessions(cls, db_session):
        print('Checking for expired sessions ...')
        now = datetime.now()
        expire_time = now - cls.EXPIRATION_TIME
        rv = db_session.query(SessionTable.id).where(SessionTable.last_touched < expire_time).all()
        for session_id in [x.id for x in rv]:
            cls._kill_session(db_session, session_id)

    @classmethod
    def _kill_session(cls, db_session, session_id):
        print(f"Deleting old session {session_id} ...")
        for stmt in [
            delete(SessionFilteredPatientTable).where(SessionFilteredPatientTable.session_id == session_id),
            delete(SessionPatientsMatchingFilterTable).where(SessionPatientsMatchingFilterTable.session_id == session_id),
            delete(SessionFilteredCaseIdTable).where(SessionFilteredCaseIdTable.session_id == session_id),
            delete(SessionTable).where(SessionTable.id == session_id),
        ]:
            db_session.execute(stmt)
        db_session.commit()
