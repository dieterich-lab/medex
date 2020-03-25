import psycopg2.extras
import numpy as np
import pandas as pd
from modules import config as con




def get_categorical_entities(rdb):
    sql ="""select column_name from INFORMATION_SCHEMA.COLUMNS where table_name = 'patients_test3' and data_type = 'text' and  not column_name = 'Patient_ID' """
    conn = None

    # connect to the PostgreSQL database
#    conn = psycopg2.connect(**rdb)
    # create a new cursor
    cur = rdb.cursor()
    # execute the INSERT statement
    cur.execute(sql)
    rows = cur.fetchall()
    # commit the changes to the database
    rdb.commit()
    # close communication with the database
    cur.close()
    res = [''.join(i) for i in rows]
    return res

def get_values(entity, r):

    entity = '"' + '","'.join(entity) + '"'

    sql = """select "Patient_ID",{} from patients_test3""".format(entity)
    conn = None

    # connect to the PostgreSQL database
#    conn = psycopg2.connect(**r)
    # create a new cursor
    cur = r.cursor()
    # execute the INSERT statement
    cur.execute(sql)
    rows = cur.fetchall()
    df = pd.read_sql(sql,r)
    # commit the changes to the database
    r.commit()
    # close communication with the database
    cur.close()

    return df


def get_numeric_entities(rdb):
    sql = "select column_name from INFORMATION_SCHEMA.COLUMNS where table_name = 'patients_test3' and data_type = 'double precision'"

    cur = rdb.cursor()
    # execute the INSERT statement
    cur.execute(sql)
    rows = cur.fetchall()
    # commit the changes to the database
    rdb.commit()
    # close communication with the database
    cur.close()
    res = [''.join(i) for i in rows]

    return res






"""
sql = "select column_name,data_type from INFORMATION_SCHEMA.COLUMNS where table_name = 'patients_test' and data_type = 'numeric'"
conn = None
try:
    # read database configuration
    params = con.config()

    # connect to the PostgreSQL database
    conn = psycopg2.connect("postgresql://postgres:12345@localhost:5432/test_patient")
    
    # create a new cursor
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql)
    rows = cur.fetchall()
    # commit the changes to the database
    conn.commit()
    # close communication with the database
    cur.close()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if conn is not None:
        conn.close()

m = np.array(rows)
# k = m.mean()
"""
