from modules.models import Sessions
from datetime import datetime


class SessionService:
    def __init__(self, database_session, session_id: str):
        self.database_session = database_session
        self.session_id = session_id

    def touch(self):
        db = self.database_session
        session = db.query(Sessions).get(self.session_id)
        now = datetime.now()
        if session is None:
            session = Sessions(
                id=self.session_id,
                created=now,
                last_touched=now
            )
            db.add(session)
        else:
            session.last_touched = now
        db.commit()

    def get_id(self):
        return self.session_id
