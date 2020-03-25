import psycopg2.extras
import numpy as np
from modules import config as con
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


try:
    conn = psycopg2.connect(user = "postgres",
                            password = "12345",
                            host = "127.0.0.1",
                            port = "5432")
    # create a new cursor
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("""CREATE DATABASE python_db""")
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)