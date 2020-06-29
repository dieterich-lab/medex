###
#   This module contains functions for creating tables in PostgreSQL database

###
from db import rdb

def create_table(header):
    """Remove tables from database if exists and create new name_type and examination tables in the PostgreSQL database"""

    sql1 = "DROP TABLE IF EXISTS name_type,examination,examination_categorical,examination_numerical,patient"

    statment_entities = """CREATE TABLE name_type ("Key" text Primary key, "type" text)"""
    try:
        # create table examination using header file
        with open(header, 'r') as in_file:
            statment_examination = "CREATE TABLE examination ("
            for line in in_file:
                statment_examination = statment_examination + '{}'.format(line)
            statment_examination = statment_examination + ")"
        in_file.close()

        cur = rdb.cursor()
        cur.execute(sql1)
        cur.execute(statment_entities)
        cur.execute(statment_examination)
        rdb.commit()
    except Exception:
        return print("Problem with connection with database")


def load_data(entities,dataset,header):
    """ Load data from entities.csv, data.csv files into examination table in PostgreSQL  """

    try:
        cur = rdb.cursor()
        # load data from entites file to name_type table
        with open(entities, 'r') as in_file:
            for row in in_file:
                row = row.replace("\n", "").split(",")
                cur.execute("INSERT INTO name_type VALUES (%s, %s) ON CONFLICT DO NOTHING",row)
        rdb.commit()
        in_file.close()

        # check how many column has table examination and create col
        a=[]
        with open(header) as in_file:
            row_count = sum(1 for row in in_file)
        in_file.close()
        for i in range(row_count):
            a.append('%s')
        col = ','.join(a)


        with open(dataset, 'r') as in_file:
            i = 0
            for row in in_file:
                i += 1
                # join values by ';' if column value has more the one value
                n = row_count - 2
                row = row.replace("\n", "").split(",")
                line = [i] + row[0:n] + [";".join([str(x) for x in row[n:]])]

                # insert data from dataset.csv to table examnination
                cur.execute("INSERT INTO examination VALUES ("+col+")",line)
        rdb.commit()
        in_file.close()
        print('stop')
    except Exception:
        return print("Problem with connection with database")

def alter_table():
    """ Divide table examination on categorical and numerical, create index for "Key" column in categorical and numerical tables """

    sql1 = """CREATE TABLE examination_categorical AS SELECT e.* from examination as e join name_type as n
            on e."Key" = n."Key" where n."type" = 'String'"""
    sql2 = """CREATE TABLE examination_numerical AS SELECT e.* from examination as e join name_type as n
                on e."Key" = n."Key" where n."type" = 'Double'"""
    sql3 = """CREATE TABLE Patient AS select distinct "Patient_ID" from examination_numerical"""

    sql4 = """ALTER TABLE examination_numerical ALTER COLUMN "Value" Type double precision Using ("Value"::double precision)"""

    sql5 = """CREATE INDEX IF NOT EXISTS "Key_index_numerical" ON examination_numerical ("Key")"""
    sql6 = """CREATE INDEX IF NOT EXISTS "Key_index_categorical" ON examination_categorical ("Key")"""

    sql7 = """CREATE EXTENSION IF NOT  EXISTS tablefunc"""
    sql8 = """DROP TABLE examination"""

    try:
        cur = rdb.cursor()
        cur.execute(sql1)
        cur.execute(sql2)
        cur.execute(sql3)
        cur.execute(sql4)
        cur.execute(sql5)
        cur.execute(sql6)
        cur.execute(sql7)
        cur.execute(sql8)
        rdb.commit()
    except Exception:
        return print("Problem with connection with database")




















