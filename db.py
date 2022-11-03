from flask import g
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from medex.services.database import get_database_url


def connect_db():
    if 'db' not in g:
        g.db = create_engine(get_database_url(), echo=False, poolclass=NullPool)


def close_db():
    if 'db' in g:
        db = g.pop('db')
        if db is not None:
            db.close()
