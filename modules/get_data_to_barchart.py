from modules.models import TableCategorical
from sqlalchemy.sql import select, distinct
from sqlalchemy import and_, literal_column, func
import pandas as pd
from modules.filtering import checking_filter, checking_date_filter


def get_bar_chart(categorical_entities, measurement, date_filter, limit_filter, update_filter, r):
    values = checking_date_filter(date_filter, TableCategorical)
    subquery = select(func.string_agg(distinct(TableCategorical.value), literal_column("'<br>'")).label('value'),
                      TableCategorical.measurement)
    subquery = checking_filter(update_filter, TableCategorical, subquery)
    subquery = subquery.where(and_(TableCategorical.key == categorical_entities[0],
                                   TableCategorical.value.in_(categorical_entities[1]),
                                   TableCategorical.measurement.in_(measurement), values)).\
        group_by(TableCategorical.name_id, TableCategorical.measurement)

    if limit_filter.get('selected') is not None:
        subquery = subquery.limit(limit_filter.get('limit')).offset(limit_filter.get('offset'))

    sql = select(subquery.c.value.label(categorical_entities[0]), subquery.c.measurement,
                 func.count(subquery.c.value).label('count')).group_by(subquery.c.value, subquery.c.measurement)

    try:
        df = pd.read_sql(sql, r.connection())
        if df.empty:
            return df, "The entity wasn't measured"
        else:
            df.columns = [categorical_entities[0], 'measurement', 'count']
            df[categorical_entities[0]] = df[categorical_entities[0]].str.wrap(30).replace(to_replace=[r"\\n", "\n"],
                                                                                           value=["<br>", "<br>"],
                                                                                           regex=True)
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"
