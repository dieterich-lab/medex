from modules.models import TableNumerical
from sqlalchemy.sql import select
from sqlalchemy import text
import pandas as pd
from modules.filtering import checking_filter


def get_heat_map(entities, date_filter, limit_filter, update_filter, r):
    case_when = ""
    for i in entities:
        case_when += """ min(CASE WHEN key = $${0}$$ then value end) as "{0}",""".format(i)
    case_when = case_when[:-1]

    sql = select(TableNumerical.name_id, text(case_when))
    sql = checking_filter(update_filter, TableNumerical, sql)

    if date_filter[2] != 0:
        sql = sql.where(TableNumerical.date.between(date_filter[3], date_filter[4]))

    sql = sql.group_by(TableNumerical.name_id)

    if limit_filter.get('selected') is not None:
        sql = sql.limit(limit_filter['limit']).offset(limit_filter['offset'])

    try:
        df = pd.read_sql(sql, r.connection())
        if df.empty:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"
