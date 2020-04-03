import pandas as pd





def get_categorical_entities(rdb):
    sql ="""select column_name from INFORMATION_SCHEMA.COLUMNS where table_name = 'patients_test2' and data_type = 'text' and  not column_name = 'Patient_ID' """

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

def get_values_basic_stats(entity, r):

    entity_fin = '"' + '","'.join(entity) + '"'


    sql = """select "Patient_ID",{} from patients_test2 """.format(entity_fin)

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



def get_values(entity, r):

    entity_fin = '"' + '","'.join(entity) + '"'
    strin ='"' + '" IS NOT NULL AND "'.join(entity) + '" IS NOT NULL'

    sql = """select "Patient_ID",{} from patients_test2 where {} """.format(entity_fin,strin)

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
    sql = "select column_name from INFORMATION_SCHEMA.COLUMNS where table_name = 'patients_test2' and data_type = 'double precision'"

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

