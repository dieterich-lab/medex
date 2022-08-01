from modules.models import TableNumerical
from sqlalchemy.sql import select
from sqlalchemy.sql import join
from sqlalchemy import text, case, func
import pandas as pd
from modules.filtering import checking_date_filter, apply_limit_to_sql_query


def get_heat_map(entities, date_filter, limit_filter, update_filter, session_db):
    case_when = [func.min(case([(TableNumerical.key == i, TableNumerical.value)])).label(i) for i in entities]
    sql = select(TableNumerical.name_id, *case_when).where(checking_date_filter(date_filter, TableNumerical)).\
        group_by(TableNumerical.name_id)
    sql_with_filter = apply_filter_heatmap(sql, update_filter)
    sql_limit = apply_limit_to_sql_query(limit_filter, sql_with_filter)
    df = pd.read_sql(sql_limit, session_db.connection())
    return df, None


def apply_filter_heatmap(sql, update_filter):
    if update_filter['filter_update'] != 0:
        cte = sql.cte('cte')
        j = join(cte, text("temp_table_name_ids"),
                 cte.c.name_id == text("temp_table_name_ids.name_id"))
        sql_with_filter = select(cte.c).select_from(j)
    else:
        sql_with_filter = sql
    return sql_with_filter
