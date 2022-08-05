from modules.models import TableNumerical, TableCategorical
from sqlalchemy.sql import select
from sqlalchemy import and_, func
import pandas as pd
from modules.filtering import apply_filter_to_sql, checking_date_filter, apply_limit_to_sql_query


def get_histogram_box_plot(entities, measurement, date_filter, limit_filter, update_filter, session_db):
    sql_select = select(TableNumerical.name_id, TableNumerical.measurement,
                        func.avg(TableNumerical.value).label(entities[0]),
                        TableCategorical.value.label(entities[1]))
    sql_with_filter = apply_filter_to_sql(update_filter, TableNumerical, sql_select)
    sql_with_where = sql_with_filter.where(and_(TableNumerical.key == entities[0], TableCategorical.key == entities[1],
                                                TableCategorical.value.in_(entities[2]),
                                                TableNumerical.measurement.in_(measurement),
                                                checking_date_filter(date_filter, TableNumerical),
                                                TableCategorical.name_id == TableNumerical.name_id)).\
        group_by(TableNumerical.name_id, TableNumerical.measurement, TableCategorical.value)

    sql_limit = apply_limit_to_sql_query(limit_filter, sql_with_where)

    df = pd.read_sql(sql_limit, session_db.connection())
    df[entities[1]] = df[entities[1]].str.wrap(30).replace(to_replace=[r"\\n", "\n"], value=["<br>", "<br>"],
                                                           regex=True)
    return df, None

