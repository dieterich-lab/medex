"""
    This module contains functions for creating tables in PostgreSQL database
"""

import time
import re


def is_date(date):
    if re.match("^(0[0-9]{2}[1-9]|[1-9][0-9]{3})-((0[13578]|10|12)-(0[1-9]|[12][0-9]|3[01])|02-(0[1-9]|1[0-9]|2[0-8])|(0[469]|11)-(0[1-9]|[12][0-9]|30))$",date) is None:
        return False
    else:
        return True


def create_table(rdb):
    """
    Remove tables from database if exists and create new name_type and examination tables in the PostgreSQL database
    """

    sql_drop = "DROP TABLE IF EXISTS header,name_type,examination,examination_categorical,examination_numerical," \
               "examination_date,patient"

    statement_header = """CREATE TABLE header ("Name_ID" text Primary key,
                                                "measurement" text)"""

    statement_entities = """CREATE TABLE name_type ("order" numeric,
                                                    "Key" text Primary key,
                                                    "type" text,
                                                    "synonym" text,
                                                    "description" text,
                                                    "unit" text,
                                                    "show" text)"""

    examination_numerical = """CREATE TABLE examination_numerical (
                                "ID" numeric PRIMARY KEY,
                                "Name_ID" text,
                                "Case_ID" text,
                                measurement text,
                                "Date" text,
                                "Time" text,
                                "Key" text,
                                "Value" double precision)"""

    examination_date = """CREATE TABLE examination_date (
                                "ID" numeric PRIMARY KEY,
                                "Name_ID" text,
                                "Case_ID" text,
                                measurement text,
                                "Date" text,
                                "Time" text,
                                "Key" text,
                                "Value" text)"""

    examination_categorical = """CREATE TABLE examination_categorical (
                                "ID" numeric PRIMARY KEY,
                                "Name_ID" text,
                                "Case_ID" text,
                                measurement text,
                                "Date" text,
                                "Time" text,
                                "Key" text,
                                "Value" text)"""

    try:
        cur = rdb.cursor()
        cur.execute(sql_drop)
        cur.execute(statement_header)
        cur.execute(statement_entities)
        cur.execute(examination_numerical)
        cur.execute(examination_categorical)
        cur.execute(examination_date)
        rdb.commit()
    except Exception:
        return print("Problem with connection with database")


def load_data(entities, dataset, header, rdb):
    """
    Load data from entities.csv, data.csv,header.csv files into examination table in Postgresql
    """

    cur = rdb.cursor()

    # load data from header.csv file to header table

    cur.execute("INSERT INTO header VALUES (%s, %s) ON CONFLICT DO NOTHING", [header[0], header[2]])

    # load data from entities.csv file to name_type table
    with open(entities, 'r') as in_file:
        head = next(in_file)
        if 'order' in head:
            for row in in_file:
                row = row.replace("\n", "").split(",")
                if len(row) == 3:
                    cur.execute("INSERT INTO name_type VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", row)
                elif len(row) == 4:
                    cur.execute("INSERT INTO name_type VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", row)
                elif len(row) == 5:
                    cur.execute("INSERT INTO name_type VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", row)
                elif len(row) == 6:
                    cur.execute("INSERT INTO name_type VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", row)
                elif len(row) == 7:
                    cur.execute("INSERT INTO name_type VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", row)
                else:
                    print("This line doesn't have appropriate format:", row)
        else:
            i = 0
            for row in in_file:
                i += 1
                row = row.replace("\n", "").split(",")
                line = [i] + row[:]
                if len(line) == 3:
                    cur.execute("INSERT INTO name_type VALUES (%s,%s,%s) ON CONFLICT DO NOTHING", line)
                elif len(line) == 4:
                    cur.execute("INSERT INTO name_type VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING", line)
                elif len(line) == 5:
                    cur.execute("INSERT INTO name_type VALUES (%s,%s,%s, %s,%s) ON CONFLICT DO NOTHING", line)
                elif len(line) == 6:
                    cur.execute("INSERT INTO name_type VALUES (%s,%s,%s,%s, %s,%s) ON CONFLICT DO NOTHING", line)
                elif len(line) == 7:
                    cur.execute("INSERT INTO name_type VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", line)
                else:
                    print("This line doesn't have appropriate format:", row)
    rdb.commit()
    in_file.close()
    with open(dataset, 'r', encoding="utf8", errors='ignore') as in_file:
        i = 0
        for row in in_file:
            i += 1
            row = row.rstrip().replace('"', "").replace("\n", "").split(",")
            # insert data from dataset.csv to table examination
            if 'Visit' in header:
                line = [i] + row[0:6] + [";".join([str(x) for x in row[6:]])]
            else:
                line = [i] + row[0:2] + [1] + row[2:5] + [";".join([str(x) for x in row[5:]])]
            if len(line) < 7:
                print("This line doesn't have appropriate format:", line)
            else:
                try:
                    if line[7].lstrip('-').replace('.', '', 1).isdigit():
                        cur.execute("INSERT INTO examination_numerical VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", line)
                    elif is_date(line[7]):
                        cur.execute("INSERT INTO examination_date VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", line)
                    else:
                        cur.execute("INSERT INTO examination_categorical VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", line)

                except:
                    print(line)

    rdb.commit()
    in_file.close()


def alter_table(rdb):
    """
    Divide table examination on categorical and numerical, create index for "Key" column in categorical and numerical
    tables
    """

    sql_remove_null = """DELETE FROM examination_categorical WHERE "Value" is null """

    sql4 = """CREATE TABLE Patient AS select distinct "Name_ID","Case_ID" from 
                        (SELECT "Name_ID","Case_ID" FROM examination_numerical
                         UNION
                         SELECT "Name_ID","Case_ID" FROM examination_date
                         UNION
                         SELECT "Name_ID","Case_ID" FROM examination_categorical) as foo"""

    sql5 = """ALTER TABLE patient ADD CONSTRAINT patient_pkey PRIMARY KEY ("Name_ID")"""
    sql8 = """ALTER TABLE examination_categorical ADD CONSTRAINT forgein_key_c2 FOREIGN KEY ("Name_ID") REFERENCES 
    patient ("Name_ID")"""
    sql9 = """ALTER TABLE examination_numerical ADD CONSTRAINT forgein_key_n2 FOREIGN KEY ("Name_ID") REFERENCES 
    patient ("Name_ID")"""
    sql10 = """ALTER TABLE examination_categorical ADD CONSTRAINT forgein_key_c1 FOREIGN KEY ("Key") REFERENCES 
    name_type ("Key")"""
    sql11 = """ALTER TABLE examination_numerical ADD CONSTRAINT forgein_key_n1 FOREIGN KEY ("Key") REFERENCES 
    name_type ("Key")"""

    sql12 = """CREATE INDEX IF NOT EXISTS "Key_index_numerical" ON examination_numerical ("Key")"""
    sql13 = """CREATE INDEX IF NOT EXISTS "Key_index_categorical" ON examination_categorical ("Key")"""
    sql15 = """CREATE INDEX IF NOT EXISTS "ID_index_numerical" ON examination_numerical ("Name_ID")"""
    sql16 = """CREATE INDEX IF NOT EXISTS "ID_index_categorical" ON examination_categorical ("Name_ID")"""
    sql17 = """CREATE INDEX IF NOT EXISTS "case_index_patient" ON Patient ("Case_ID")"""
    sql18 = """CREATE INDEX IF NOT EXISTS "ID_index_patient" ON Patient ("Name_ID")"""
    sql19 = """CREATE INDEX IF NOT EXISTS "ID_index_date" ON examination_numerical ("Name_ID")"""
    sql14 = """CREATE EXTENSION IF NOT EXISTS tablefunc"""

    try:
        cur = rdb.cursor()
        cur.execute(sql_remove_null)
        cur.execute(sql4)
    except Exception:
        return print("Problem with connection with database")
    try:
        cur.execute(sql5)
        cur.execute(sql8)
        cur.execute(sql9)
        cur.execute(sql10)
        cur.execute(sql11)
    except Exception:
        return print("Problem with connection with database")
    try:
        cur.execute(sql12)
        cur.execute(sql13)
        cur.execute(sql14)
        cur.execute(sql15)
        cur.execute(sql16)
        cur.execute(sql17)
        cur.execute(sql18)
        cur.execute(sql19)
        rdb.commit()
    except Exception:
        return print("Problem with connection with database")




















