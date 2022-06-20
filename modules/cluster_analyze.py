def cluster_table(rdb):
    with rdb.connect() as conn:
        try:
            conn.execute(""" CLUSTER examination_date USING key_index_date """)
            conn.execute(""" CLUSTER examination_numerical USING key_index_numerical """)
            conn.execute(""" CLUSTER examination_categorical USING key_index_categorical """)
        except (Exception,):
            return print("Problem with connection with database")


def analyze_table(rdb):
    with rdb.connect() as conn:
        try:
            conn.execute(""" ANALYZE examination_numerical""")
            conn.execute(""" ANALYZE examination_categorical""")
            conn.execute(""" ANALYZE examination_date""")
        except (Exception,):
            return print("Problem with connection with database")


def alter_system(rdb):
    with rdb.connect() as conn:
        try:
            conn.execute(""" ALTER SYSTEM SET work_mem='2GB' """)
            conn.execute(""" ALTER SYSTEM SET max_parallel_workers_per_gather=7 """)
        except (Exception,):
            return print("Problem with connection with database")
