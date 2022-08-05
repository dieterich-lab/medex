def cluster_table(rdb):
    with rdb.connect() as conn:
        try:
            conn.execute(""" CLUSTER examination_date USING idx_key_date""")
            conn.execute(""" CLUSTER examination_numerical USING idx_key_num""")
            conn.execute(""" CLUSTER examination_categorical USING idx_key_cat""")
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
    with rdb.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        try:
            conn.execute(""" ALTER SYSTEM SET work_mem='2GB' """)
            conn.execute(""" ALTER SYSTEM SET max_parallel_workers_per_gather=7 """)
        except (Exception,):
            return print("Problem with connection with database")
