"""
    This module contains functions for creating tables in PostgreSQL database
"""

import re
import pandas as pd
import logging

logging.basicConfig()


def is_date(date):
    if re.match("^(0[0-9]{2}[1-9]|[1-9][0-9]{3})-((0[13578]|10|12)-(0[1-9]|[12][0-9]|3[01])|02-(0[1-9]|1[0-9]|2[0-9])"
                "|(0[469]|11)-(0[1-9]|[12][0-9]|30))$", date) is None:
        return False
    else:
        return True


def create_table(rdb):
    """
    Remove tables from database if exists and create new name_type and examination tables in the PostgreSQL database
    """

    sql_drop = "DROP TABLE IF EXISTS header,name_type,examination,examination_categorical,examination_numerical," \
               "examination_date,patient"

    statement_header = """CREATE TABLE header (name_id text Primary key,
                                                measurement text)"""

    statement_entities = """CREATE TABLE name_type (orders numeric,
                                                    key text Primary key,
                                                    type text,
                                                    synonym text,
                                                    description text,
                                                    unit text,
                                                    show text)"""

    examination_numerical = """CREATE TABLE examination_numerical (
                                id numeric PRIMARY key,
                                name_id text,
                                case_id text,
                                measurement text,
                                date text,
                                time text,
                                key text,
                                value double precision)"""

    examination_date = """CREATE TABLE examination_date (
                                id numeric PRIMARY key,
                                name_id text,
                                case_id text,
                                measurement text,
                                date text,
                                time text,
                                key text,
                                value text)"""

    examination_categorical = """CREATE TABLE examination_categorical (
                                id numeric PRIMARY key,
                                name_id text,
                                case_id text,
                                measurement text,
                                date text,
                                time text,
                                key text,
                                value text)"""

    try:
        with rdb.connect() as conn:
            conn.execute(sql_drop)
            conn.execute(statement_header)
            conn.execute(statement_entities)
            conn.execute(examination_numerical)
            conn.execute(examination_categorical)
            conn.execute(examination_date)
    except (Exception,):
        return print("Problem with connection with database")


def load_data(entities, dataset, header, rdb):
    """
    Load data from entities.csv, data.csv,header.csv files into examination table in Postgresql
    """


    # load data from header.csv file to header table
    with rdb.connect() as conn:
        conn.execute("INSERT INTO header values (%s, %s) ON CONFLICT DO NOTHING", [header[0], header[2]])

        # load data from entities.csv file to name_type table
        with open(entities, 'r') as in_file:
            head = next(in_file)
            i = 0
            for row in in_file:
                row = row.replace("  ", " ").replace("\n", "").split(",")
                if 'order' not in head:
                    i += 1
                    row = [str(i)] + row
                    if len(row) == 3:
                        conn.execute("INSERT INTO name_type values (%s, %s, %s) ON CONFLICT DO NOTHING", row)
                    elif len(row) == 4:
                        conn.execute("INSERT INTO name_type values (%s, %s, %s, %s) ON CONFLICT DO NOTHING", row)
                    elif len(row) == 5:
                        conn.execute("INSERT INTO name_type values (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", row)
                    elif len(row) == 6:
                        conn.execute("INSERT INTO name_type values (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", row)
                    elif len(row) == 7:
                        conn.execute("INSERT INTO name_type values (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", row)
        in_file.close()
        df = pd.read_csv(entities)
        numerical_entities = df[df['type'] == 'Double']['Key']
        numerical_entities = numerical_entities.to_list()
        date_entities = df[df['type'] == 'date']['Key']
        date_entities = date_entities.to_list()
        with open(dataset, 'r', encoding="utf8", errors='ignore') as in_file:
            i = 0
            for row in in_file:
                i += 1
                row = row.rstrip().replace('"', "").replace("\n", "").split(",")
                if 'Visit' in header:
                    line = [str(i)] + row[0:6] + [";".join([str(x) for x in row[6:]])]
                else:
                    line = [str(i)] + row[0:2] + ['1'] + row[2:5] + [";".join([str(x) for x in row[5:]])]
                if len(line) < 7:
                    print("This line doesn't have appropriate format:", line)
                else:
                    try:
                        line[6] = line[6].replace("  ", " ")
                        if line[7].replace('.', '', 1).isdigit() and line[6] in numerical_entities:
                            conn.execute("INSERT INTO examination_numerical values (%s,%s,%s,%s,%s,%s,%s,%s)", line)
                        elif line[6] in date_entities:
                            conn.execute("INSERT INTO examination_date values (%s,%s,%s,%s,%s,%s,%s,%s)", line)
                        else:
                            conn.execute("INSERT INTO examination_categorical values (%s,%s,%s,%s,%s,%s,%s,%s)", line)
                    except (Exception,):
                        print(line)

        in_file.close()


def alter_table(rdb):
    """
    Divide table examination on categorical and numerical, create index for "key" column in categorical and numerical
    tables
    """

    sql_remove_null = """DELETE FROM examination_categorical WHERE value is null """

    sql = """CREATE TABLE Patient AS select distinct name_id,case_id from 
                        (SELECT name_id,case_id FROM examination_numerical
                         UNION
                         SELECT name_id,"case_id" FROM examination_date
                         UNION
                         SELECT name_id,case_id FROM examination_categorical) as foo"""

    sql4 = """ALTER TABLE examination_categorical ADD CONSTRAINT forgein_key_c1 FOREIGN key (key) REFERENCES 
    name_type (key)"""
    sql5 = """ALTER TABLE examination_numerical ADD CONSTRAINT forgein_key_n1 FOREIGN key (key) REFERENCES 
    name_type (key)"""
    with rdb.connect() as conn:
        try:
            conn.execute(sql_remove_null)
            conn.execute(sql)
        except (Exception,):
            return print("Problem with connection with database")
        try:
            conn.execute(sql4)
            conn.execute(sql5)
        except (Exception,):
            return print("Problem with connection with database")


def create_index(rdb):

    sql1 = """CREATE INDEX IF NOT EXISTS key_index_numerical ON examination_numerical (key)"""
    sql2 = """CREATE INDEX IF NOT EXISTS key_index_categorical ON examination_categorical (key)"""
    sql3 = """CREATE INDEX IF NOT EXISTS key_index_date ON examination_date (key)"""

    sql4 = """CREATE INDEX IF NOT EXISTS id_index_numerical ON examination_numerical (name_id)"""
    sql5 = """CREATE INDEX IF NOT EXISTS id_index_categorical ON examination_categorical (name_id)"""
    sql6 = """CREATE INDEX IF NOT EXISTS id_index_date ON examination_date (name_id)"""

    sql7 = """CREATE INDEX IF NOT EXISTS case_index_patient ON Patient (case_id)"""
    sql8 = """CREATE INDEX IF NOT EXISTS id_index_patient ON Patient (name_id)"""
    sql9 = """CREATE EXTENSION IF NOT EXISTS tablefunc"""
    with rdb.connect() as conn:
        try:
            conn.execute(sql1)
            conn.execute(sql2)
            conn.execute(sql3)
            conn.execute(sql4)
            conn.execute(sql5)
            conn.execute(sql6)
            conn.execute(sql7)
            conn.execute(sql8)
            conn.execute(sql9)
        except (Exception,):
            return print("Problem with connection with database")


def cluster_table(rdb):
    # Vacuum analyze
    sql1 = """ VACUUM """

    # CLUSTER tables
    sql2 = """ CLUSTER examination_date USING key_index_date """
    sql3 = """ CLUSTER examination_numerical USING key_index_numerical """
    sql4 = """ CLUSTER examination_categorical USING key_index_categorical """

    # Analyze
    sql5 = """ ANALYZE examination_numerical"""
    sql6 = """ ANALYZE examination_categorical"""
    sql7 = """ ANALYZE examination_date"""

    sql8 = """ ALTER SYSTEM SET work_mem='2GB' """
    sql9 = """ ALTER SYSTEM SET max_parallel_workers_per_gather=7 """
    with rdb.connect() as conn:
        try:
            conn.autocommit = True
            conn.execute(sql1)
            conn.execute(sql2)
            conn.execute(sql3)
            conn.execute(sql4)
            conn.execute(sql5)
            conn.execute(sql6)
            conn.execute(sql7)
            conn.execute(sql8)
            conn.execute(sql9)
        except (Exception,):
            return print("Problem with connection with database")
