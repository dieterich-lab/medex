from sqlalchemy import text

from medex.services.database import get_db_session, get_db_engine


def cluster_table():
    db_session = get_db_session()
    db_session.execute(text('CLUSTER examination_date USING idx_key_date'))
    db_session.execute(text('CLUSTER examination_numerical USING idx_key_num'))
    db_session.execute(text('CLUSTER examination_categorical USING idx_key_cat'))
    db_session.commit()


def analyze_table():
    db_session = get_db_session()
    db_session.execute(text('ANALYZE examination_numerical'))
    db_session.execute(text('ANALYZE examination_categorical'))
    db_session.execute(text('ANALYZE examination_date'))
    db_session.commit()


def alter_system():
    engine = get_db_engine()
    c = engine.connect().execution_options(isolation_level="AUTOCOMMIT")
    for command in [
        "ALTER SYSTEM SET work_mem='2GB'",
        "ALTER SYSTEM SET max_parallel_workers_per_gather=7",
    ]:
        c.execute(text(command))
