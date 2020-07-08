###
#   This module contains functions for creating tables in PostgreSQL database

###


def create_table():
    """Remove tables from database if exists and create new name_type and examination tables in the PostgreSQL database"""
    from webserver import rdb
    sql1 = "DROP TABLE IF EXISTS name_type,examination,examination_categorical,examination_numerical,patient"

    statment_entities = """CREATE TABLE name_type ("Key" text Primary key, "type" text)"""
    statment_examination = """CREATE tABLE examination ("ID" numeric PRIMARY KEY,
                                "Patient_ID" text,
                                "Billing_ID" text,
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


def load_data(entities, dataset):
    """ Load data from entities.csv, data.csv files into examination table in PostgreSQL  """
    from webserver import rdb
    cur = rdb.cursor()
    # load data from entites file to name_type table
    with open(entities, 'r') as in_file:
        next(in_file)
        for row in in_file:
            row = row.replace("\n", "").split(",")
            if len(row) != 2:
                print("This line doesn't have appropriate format:",row)
            else:
                cur.execute("INSERT INTO name_type VALUES (%s, %s) ON CONFLICT DO NOTHING",row)
    rdb.commit()
    in_file.close()

    with open(dataset, 'r') as in_file:
        i = 0
        for row in in_file:
            i += 1
            # join values by ';' if column value has more the one value
            row = row.rstrip()
            row = row.replace("\n", "").split(",")
            line = [i] + row[0:5] + [";".join([str(x) for x in row[5:]])]
            # insert data from dataset.csv to table examnination
            if len(row) < 6:
                print("This line doesn't have appropriate format:",row)
            else :
                cur.execute("INSERT INTO examination VALUES (%s,%s,%s,%s,%s,%s,%s)",line)
    rdb.commit()
    in_file.close()



def alter_table():
    """ Divide table examination on categorical and numerical, create index for "Key" column in categorical and numerical tables """
    from webserver import rdb
    sql0 = """Delete from examination where "Value" is null """
    sql1 = """Delete from examination as e using name_type as n where e."Key" = n."Key" and n."type" = 'Double' 
                and e."Value" = 'None'"""

    sql2 = """  CREATE TABLE examination_categorical AS SELECT min("ID") as "ID","Patient_ID","Key",min("Value") as "Value" 
                from (SELECT e.* from examination as e join name_type as n on e."Key" = n."Key" 
                where n."type" = 'String') as f  group by "Patient_ID","Key"   """
    sql3 = """CREATE TABLE examination_numerical AS SELECT min("ID") as "ID","Patient_ID","Key",AVG("Value"::double precision)
                as "Value" from (SELECT e.* from examination as e join name_type as n on e."Key" = n."Key" 
                where n."type" = 'Double') as f  group by "Patient_ID","Key" """
    sql4 = """CREATE TABLE Patient AS select distinct "Patient_ID" from examination"""

    sql5 = """ALTER TABLE patient ADD CONSTRAINT patient_pkey PRIMARY KEY ("Patient_ID")"""
    sql6 = """ALTER TABLE ONLY public.examination_numerical ADD CONSTRAINT examination_numerical_pkey PRIMARY KEY ("ID")"""
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
        cur.execute(sql1)
        cur.execute(sql2)
        cur.execute(sql3)
        cur.execute(sql4)
        cur.execute(sql5)
        cur.execute(sql6)
        cur.execute(sql7)
        cur.execute(sql8)
        cur.execute(sql9)
        cur.execute(sql10)
        cur.execute(sql11)
        cur.execute(sql12)
        cur.execute(sql13)
        rdb.commit()
    except Exception:
        return print("Problem with connection with database")




















