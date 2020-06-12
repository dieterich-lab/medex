import sys
import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())



user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
host = os.environ['POSTGRES_HOST']
database = os.environ['POSTGRES_DB']
port = os.environ['POSTGRES_PORT']
DB=f'postgresql://{user}:{password}@{host}:{port}/{database}'


def get_db(key=None):
    return getattr(get_db, 'pool').getconn(key)

def put_db(conn, key=None):
    getattr(get_db, 'pool').putconn(conn, key=key)

# So we here need to init connection pool in main thread in order everything to work
# Pool is initialized under function object get_db
try:
    setattr(get_db, 'pool', psycopg2.pool.ThreadedConnectionPool(1, 20, DB))
except psycopg2.OperationalError as e:
    print(e)
    sys.exit(0)