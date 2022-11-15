from medex.services.database import get_db_session


def cluster_table():
    db_session = get_db_session()
    db_session.execute(""" CLUSTER examination_date USING idx_key_date""")
    db_session.execute(""" CLUSTER examination_numerical USING idx_key_num""")
    db_session.execute(""" CLUSTER examination_categorical USING idx_key_cat""")


def analyze_table():
    db_session = get_db_session()
    db_session.execute(""" ANALYZE examination_numerical""")
    db_session.execute(""" ANALYZE examination_categorical""")
    db_session.execute(""" ANALYZE examination_date""")


def alter_system():
    db_session = get_db_session()
    db_session.execute(""" ALTER SYSTEM SET work_mem='2GB' """)
    db_session.execute(""" ALTER SYSTEM SET max_parallel_workers_per_gather=7 """)
