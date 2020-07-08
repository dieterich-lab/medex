from flask import g
import psycopg2.extras
import os


user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
host = os.environ['POSTGRES_HOST']
database = os.environ['POSTGRES_DB']
port = os.environ['POSTGRES_PORT']
DATABASE_URL= f'postgresql://{user}:{password}@{host}:{port}/{database}'

# Connection with database
def connect_db():
    """ connects to database """
    db = getattr(g, '_database', None)
    if db is None:
        db = psycopg2.connect(DATABASE_URL)
    return db


def close_db(e=None):
    db = g.pop('db', None)




