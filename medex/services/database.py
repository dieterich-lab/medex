import os

from sqlalchemy.orm import Session

_db_engine = None
_get_session_func = None


def get_database_url():
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    host = os.environ['POSTGRES_HOST']
    database = os.environ['POSTGRES_DB']
    port = os.environ['POSTGRES_PORT']
    url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    print(f"Database URL: {url}")
    return url


def get_db_session() -> Session:
    if _get_session_func is None:
        raise Exception("DB session not initialized!")
    else:
        return _get_session_func()


def get_db_engine():
    if _db_engine is None:
        raise Exception("DB session not initialized!")
    else:
        return _db_engine


def init_db(engine, get_session_func):
    global _db_engine, _get_session_func
    _db_engine = engine
    _get_session_func = get_session_func
