###
#   This module contains functions for creating tables in PostgreSQL database

###


def create_table(rdb):
    """Remove tables from database if exists and create new name_type and examination tables in the PostgreSQL database"""

    sql1 = "DROP TABLE IF EXISTS name_type,examination,examination_categorical,examination_numerical,patient"

    statment_entities = """CREATE TABLE name_type ("Key" text Primary key, "type" text,"description" text,"link" text)"""
    statment_examination = """CREATE tABLE examination ("ID" numeric PRIMARY KEY,
                                "Patient_ID" text,
                                "Visit" text,
                                "Date" text,
                                "Time" text,
                                "Key" text,
                                "Value" text)"""

    try:
        cur = rdb.cursor()
        cur.execute(sql1)
        cur.execute(statment_entities)
        cur.execute(statment_examination)
        rdb.commit()
    except Exception:
        return print("Problem with connection with database")


def load_data(entities, dataset,rdb):
    """ Load data from entities.csv, data.csv files into examination table in PostgreSQL  """

    cur = rdb.cursor()
    # load data from entites.csv file to name_type table
    with open(entities, 'r') as in_file:
        next(in_file)
        for row in in_file:
            row = row.replace("\n", "").split(",")
            if len(row) == 2:
                cur.execute("INSERT INTO name_type VALUES (%s, %s) ON CONFLICT DO NOTHING", row)
            elif len(row) == 3:
                cur.execute("INSERT INTO name_type VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", row)
            elif len(row) == 4:
                cur.execute("INSERT INTO name_type VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",row)
            else:
                print("This line doesn't have appropriate format:", row)
    rdb.commit()
    in_file.close()

    with open(dataset, 'r') as in_file:
        i = 0
        for row in in_file:
            i += 1
            row = row.rstrip()
            row = row.replace('"', "")
            row = row.replace("\n", "").split(",")
            # insert data from dataset.csv to table examnination
            line = [i] + row[0:6]
            if len(row) < 6:
                print("This line doesn't have appropriate format:",row)
            else:
                cur.execute("INSERT INTO examination VALUES (%s,%s,%s,%s,%s,%s,%s)", line)

    rdb.commit()
    in_file.close()



def alter_table(rdb):
    """ Divide table examination on categorical and numerical, create index for "Key" column in categorical and numerical tables """

    sql0 = """Delete from examination where "Value" is null """

    sql2 = """CREATE TABLE examination_categorical AS SELECT "ID","Patient_ID","Visit","Date","Key","Value" from
            (SELECT e.* from examination as e join name_type as n on e."Key" = n."Key" where n."type" = 'String') as f """
    sql3 = """CREATE TABLE examination_numerical AS SELECT "ID","Patient_ID","Visit","Date","Key",
                ("Value"::double precision) as "Value" from (SELECT e.* from examination as e join name_type 
                as n on e."Key" = n."Key" where n."type" = 'Double' and e."Value" ~ '^\d+(\.\d+)?$') as f """
    sql4 = """CREATE TABLE Patient AS select distinct "Patient_ID" from examination"""

    sql5 = """ALTER TABLE patient ADD CONSTRAINT patient_pkey PRIMARY KEY ("Patient_ID")"""
    sql6 = """ALTER TABLE examination_numerical ADD CONSTRAINT examination_numerical_pkey PRIMARY KEY ("ID")"""
    sql7 = """ALTER TABLE examination_categorical ADD CONSTRAINT examination_categorical_pkey PRIMARY KEY ("ID")"""
    sql8 = """ALTER TABLE examination_categorical ADD CONSTRAINT forgein_key_c2 FOREIGN KEY ("Patient_ID") REFERENCES patient ("Patient_ID")"""
    sql9 = """ALTER TABLE examination_numerical ADD CONSTRAINT forgein_key_n2 FOREIGN KEY ("Patient_ID") REFERENCES patient ("Patient_ID")"""
    sql10 = """ALTER TABLE examination_categorical ADD CONSTRAINT forgein_key_c1 FOREIGN KEY ("Key") REFERENCES name_type ("Key")"""
    sql11 = """ALTER TABLE examination_numerical ADD CONSTRAINT forgein_key_n1 FOREIGN KEY ("Key") REFERENCES name_type ("Key")"""

    sql12 = """CREATE INDEX IF NOT EXISTS "Key_index_numerical" ON examination_numerical ("Key")"""
    sql13 = """CREATE INDEX IF NOT EXISTS "Key_index_categorical" ON examination_categorical ("Key")"""

    try:
        cur = rdb.cursor()
        cur.execute(sql0)
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
        rdb.commit()
    except Exception:
        return print("Problem with connection with database")




















