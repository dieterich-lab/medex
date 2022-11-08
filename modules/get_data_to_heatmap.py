from modules.models import TableNumerical
from sqlalchemy.sql import select
from sqlalchemy import case, func
import pandas as pd
from modules.filtering import checking_date_filter, apply_limit_to_sql_query, apply_filter_heatmap


def get_heat_map(entities, date_filter, limit_filter, update_filter, session_db):
    case_when = [func.min(case([(TableNumerical.key == i, TableNumerical.value)])).label(i) for i in entities]
    sql = select(TableNumerical.name_id, *case_when).where(checking_date_filter(date_filter, TableNumerical)).\
        group_by(TableNumerical.name_id)
    sql_with_filter = apply_filter_heatmap(sql, update_filter)
    sql_limit = apply_limit_to_sql_query(limit_filter, sql_with_filter)
    df = pd.read_sql(sql_limit, session_db.connection())
    return df, None
