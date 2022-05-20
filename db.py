from flask import g
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool


user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
host = os.environ['POSTGRES_HOST']
database = os.environ['POSTGRES_DB']
port = os.environ['POSTGRES_PORT']
DATABASE_URL = f'postgresql://{user}:{password}@{host}:{port}/{database}'


def connect_db():
    if 'db' not in g:
        g.db = create_engine(DATABASE_URL, echo=False, poolclass=NullPool)
        g.db2 = create_engine(DATABASE_URL, echo=False)


def close_db():
    if 'db' in g:
        db = g.pop('db')
        if db is not None:
            db.close()
