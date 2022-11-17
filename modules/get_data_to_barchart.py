from medex.services.filter import FilterService
from modules.models import TableCategorical
from sqlalchemy.sql import select, distinct
from sqlalchemy import and_, literal_column, func
import pandas as pd
from modules.filtering import checking_date_filter, apply_limit_to_sql_query


def get_bar_chart(categorical_entities, measurement, date_filter, limit_filter, filter_service: FilterService, session_db):
    subquery = select(func.string_agg(distinct(TableCategorical.value), literal_column("'<br>'")).label('value'),
                      TableCategorical.measurement)
    subquery_apply_filter = filter_service.apply_filter(TableCategorical, subquery)
    subquery_with_where_group = subquery_apply_filter.\
        where(and_(TableCategorical.key == categorical_entities[0],
                   TableCategorical.value.in_(categorical_entities[1]),
                   TableCategorical.measurement.in_(measurement),
                   checking_date_filter(date_filter, TableCategorical))).\
        group_by(TableCategorical.name_id, TableCategorical.measurement)
    subquery_with_limit = apply_limit_to_sql_query(limit_filter, subquery_with_where_group)

    sql = select(subquery_with_limit.c.value.label(categorical_entities[0]), subquery_with_limit.c.measurement,
                 func.count(subquery_with_limit.c.value).label('count')).\
        group_by(subquery_with_limit.c.value, subquery_with_limit.c.measurement)

    df = pd.read_sql(sql, session_db.connection())
    df[categorical_entities[0]] = df[categorical_entities[0]].str.wrap(30).replace(to_replace=[r"\\n", "\n"],
                                                                                   value=["<br>", "<br>"],
                                                                                   regex=True)
    return df, None
