from modules.models import Sessions
from datetime import datetime


class SessionService:
    def __init__(self, database_session, session_id: str):
        self._database_session = database_session
        self._session_id = session_id
        self._touched_already = False

    def touch(self):
        if self._touched_already:
            return
        db = self._database_session
        session = db.query(Sessions).get(self._session_id)
        now = datetime.now()
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
        self._touched_already = True

    def get_id(self):
        return self._session_id
