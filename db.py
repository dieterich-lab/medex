from flask import g, session
import psycopg2.extras
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import time
from sqlalchemy.ext.declarative import declarative_base

user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
host = os.environ['POSTGRES_HOST']
database = os.environ['POSTGRES_DB']
port = os.environ['POSTGRES_PORT']
DATABASE_URL = f'postgresql://{user}:{password}@{host}:{port}/{database}'


# Connection with database
def connect_db():
    """ connects to database """
    db = getattr(g, '_database', None)
    while db is None:
        try:
            db = create_engine(DATABASE_URL, echo=False)
            db = db.raw_connection()
            return db
        except Exception:
            time.sleep(0.1)


def close_db(e=None):
    db = g.pop('db', None)





