from sqlalchemy.orm import Session
from datetime import datetime, timedelta

MAX_AGE = timedelta(minutes=30)


class DatabaseSessionFactory:

    class SessionItem:
        def __init__(self, db_session: Session):
            self.session = db_session
            self.last_access = None
            self.touch()

        def touch(self):
            self.last_access = datetime.now()

    def __init__(self, db_engine):
        self.db_engine = db_engine
        self.sessions_by_id = dict()

    def get_session(self, session_id: str) -> Session:
        if session_id not in self.sessions_by_id:
            new_session = Session(self.db_engine)
            self.sessions_by_id[session_id] = self.SessionItem(new_session)
        self.sessions_by_id[session_id].touch()
        self.cleanup()
        return self.sessions_by_id[session_id].session

    def cleanup(self):
        for item in list(self.sessions_by_id):
            if datetime.now() > self.sessions_by_id[item].last_access + MAX_AGE:
                del self.sessions_by_id[item]
