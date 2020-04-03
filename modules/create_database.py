import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


try:
    conn = psycopg2.connect(user = "postgres",
                            password = "12345",
                            host = "127.0.0.1",
                            port = "5432")

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("""CREATE DATABASE test_patient""")
except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)