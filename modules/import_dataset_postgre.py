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

    with rdb.connect() as conn:
        try:
            conn.execute(sql_remove_null)
            conn.execute(sql)
        except (Exception,):
            return print("Problem with connection with database")


def create_index(rdb):
    sql7 = """CREATE INDEX IF NOT EXISTS case_index_patient ON Patient (case_id)"""
    sql8 = """CREATE INDEX IF NOT EXISTS id_index_patient ON Patient (name_id)"""
    with rdb.connect()as conn:
        try:

            conn.execute(sql7)
            conn.execute(sql8)
        except (Exception,):
            return print("Problem with connection with database")

