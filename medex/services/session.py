from sqlalchemy import delete

from modules.models import Sessions, SessionFilteredNameIds, SessionNameIdsMatchingFilter, SessionFilteredCaseIds
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
        session = db.query(Sessions).get(self._session_id)
        if session is None:
            session = Sessions(
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
        now = datetime.now()
        expire_time = now - cls.EXPIRATION_TIME
        rv = db_session.query(Sessions.id).where(Sessions.last_touched < expire_time).all()
        for session_id in [x.id for x in rv]:
            cls._kill_session(db_session, session_id)

    @classmethod
    def _kill_session(cls, db_session, session_id):
        print(f"Deleting old session {session_id} ...")
        for stmt in [
            delete(Sessions).where(Sessions.id == session_id),
            delete(SessionFilteredNameIds).where(SessionFilteredNameIds.session_id == session_id),
            delete(SessionNameIdsMatchingFilter).where(SessionNameIdsMatchingFilter.session_id == session_id),
            delete(SessionFilteredCaseIds).where(SessionFilteredCaseIds.session_id == session_id)
        ]:
            db_session.execute(stmt)
        db_session.commit()

