from modules.models import TableNumerical
from sqlalchemy.sql import select
from sqlalchemy import text
import pandas as pd
from modules.filtering import apply_filter_to_sql, checking_date_filter, apply_limit_to_sql_query


def get_heat_map(entities, date_filter, limit_filter, update_filter, r):
    case_when = case_when_for_sql_statement(entities)
    sql = select(TableNumerical.name_id, text(case_when))
    sql_with_filter = apply_filter_to_sql(update_filter, TableNumerical, sql)
    sql_with_where_group = sql_with_filter.where(checking_date_filter(date_filter, TableNumerical)).\
        group_by(TableNumerical.name_id)
    sql_limit = apply_limit_to_sql_query(limit_filter, sql_with_where_group)
    df = pd.read_sql(sql_limit, r.connection())
    return df, None


def case_when_for_sql_statement(entities):
    case_when = ""
    for i in entities:
        case_when += """ min(CASE WHEN key = $${0}$$ then value end) as "{0}",""".format(i)
    case_when = case_when[:-1]
    return case_when
