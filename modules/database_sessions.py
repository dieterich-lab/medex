from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from flask import g, session
import threading
import time


MAX_AGE = timedelta(seconds=1)


def _cleanup(DatabaseSessionFactory, session_id):
    time.sleep(60*30)
    del DatabaseSessionFactory.sessions_by_id[session_id]


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
        t = threading.Thread(target=_cleanup, args=(self, session_id))
        t.start()
        return self.sessions_by_id[session_id].session


def get_database_session() -> Session:
    return g.database_session_factory.get_session(session.get('session_id'))
