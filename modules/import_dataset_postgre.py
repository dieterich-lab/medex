"""
    This module contains functions for creating tables in PostgreSQL database
"""


def create_table(rdb):
    """
    Remove tables from database if exists and create new name_type and examination tables in the PostgreSQL database
    """

    sql_drop = "DROP TABLE IF EXISTS header,name_type,examination,examination_categorical,examination_numerical,patient"
    statement_header = """CREATE TABLE header ("Name_ID" text Primary key,
                                                "measurement" text)"""

    statement_entities = """CREATE TABLE name_type ("order" numeric,
                                                    "Key" text Primary key,
                                                    "type" text,
                                                    "synonym" text,
                                                    "unit" text,
                                                    "description" text,
                                                    "show" text)"""

    statement_examination = """CREATE TABLE examination (
                                "ID" numeric PRIMARY KEY,
                                "Name_ID" text,
                                measurement text,
                                "Case_ID" text,
                                "Date" text,
                                "Time" text,
                                "Key" text,
                                "Value" text)"""
    try:
        cur = rdb.cursor()
        cur.execute(sql_drop)
        cur.execute(statement_header)
        cur.execute(statement_entities)
        cur.execute(statement_examination)
        rdb.commit()
    except Exception:
        return print("Problem with connection with database")


def load_data(entities, dataset,header,rdb):
    """
    Load data from entities.csv, data.csv,header.csv files into examination table in Postgresql
    """

    cur = rdb.cursor()

    # load data from header.csv file to header table
    cur.execute("INSERT INTO header VALUES (%s, %s) ON CONFLICT DO NOTHING", header)

    # load data from entities.csv file to name_type table
    with open(entities, 'r') as in_file:
        head = next(in_file)
        if 'order' in head:
            for row in in_file:
                row = row.replace("\n", "").split(",")
                if len(row) == 3:
                    cur.execute("INSERT INTO name_type VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", row)
                elif len(row) == 4:
                    cur.execute("INSERT INTO name_type VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",row)
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
            row = row.rstrip()
            row = row.replace('"', "")
            row = row.replace("\n", "").split(",")
            # insert data from dataset.csv to table examination
            line = [i] + row[0:1]+ [1] +row[1:5] + [";".join([str(x) for x in row[5:]])]
            if len(line) < 6:
                print("This line doesn't have appropriate format:", line)
            else:
                try:
                    cur.execute("INSERT INTO examination VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", line)
                except:
                    print(line)

    rdb.commit()
    in_file.close()


def alter_table(rdb):
    """
    Divide table examination on categorical and numerical, create index for "Key" column in categorical and numerical
    tables
    """

    sql_remove_null = """Delete from examination where "Value" is null """

    sql2 = """CREATE TABLE examination_categorical as select min("ID") as "ID","Name_ID","measurement","Date" ,"Key",
    array_agg("Value") as "Value" from (SELECT e.* from examination as e join name_type as n on e."Key" 
    = n."Key" where n."type" = 'String') as f group by "Name_ID","Date","measurement","Key" order by "Name_ID" """

    sql3 = """CREATE TABLE examination_numerical AS SELECT min("ID") as "ID","Name_ID","measurement","Date","Key",
    array_agg("Value"::double precision) as "Value" from (SELECT e.* from examination as e join name_type
    as n on e."Key" = n."Key" where n."type" = 'Double' and e."Value" ~ '^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$') 
    as f group by "Name_ID","Date","measurement","Key" order by "Name_ID" """

    sql4 = """CREATE TABLE Patient AS select distinct "Name_ID","Case_ID" from examination"""

    sql5 = """ALTER TABLE patient ADD CONSTRAINT patient_pkey PRIMARY KEY ("Name_ID")"""
    sql6 = """ALTER TABLE examination_numerical ADD CONSTRAINT examination_numerical_pkey PRIMARY KEY ("ID")"""
    sql7 = """ALTER TABLE examination_categorical ADD CONSTRAINT examination_categorical_pkey PRIMARY KEY ("ID")"""
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
    sql14 = """CREATE EXTENSION IF NOT EXISTS tablefunc"""

    try:
        cur = rdb.cursor()
        cur.execute(sql_remove_null)
        cur.execute(sql2)
        cur.execute(sql3)
        cur.execute(sql4)
    except Exception:
        return print("Problem with connection with database")
    try:
        cur.execute(sql5)
        cur.execute(sql6)
        cur.execute(sql7)
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
        rdb.commit()
    except Exception:
        return print("Problem with connection with database")




















