from modules.models import TableNumerical, TableCategorical
from sqlalchemy.sql import select, distinct
from sqlalchemy.orm import aliased
from sqlalchemy import and_, literal_column, func
import pandas as pd
from modules.filtering import checking_filter, checking_date_filter


def get_scatter_plot(add_group_by, axis, measurement, categorical_entities, date_filter, limit_filter, update_filter,
                     r):
    values = checking_date_filter(date_filter, TableNumerical)
    adalias2 = aliased(TableNumerical)

    if not add_group_by:
        sql = select(TableNumerical.name_id, func.avg(TableNumerical.value).label(f'{axis[0]}_{measurement[0]}'),
                     func.avg(adalias2.value).label(f'{axis[1]}_{measurement[1]}'))
        sql = checking_filter(update_filter, TableNumerical, sql)
        sql = sql.where(and_(TableNumerical.key == axis[0], TableNumerical.measurement == measurement[0],
                             adalias2.key == axis[1], adalias2.measurement == measurement[1],
                             TableNumerical.name_id == adalias2.name_id, values)). \
            group_by(TableNumerical.name_id)
    else:
        subquery = select(TableNumerical.name_id, TableNumerical.value.label('value1'), adalias2.value.label('value2'))
        subquery = checking_filter(update_filter, TableNumerical, subquery)
        subquery = subquery.where(and_(TableNumerical.key == axis[0], TableNumerical.measurement == measurement[0],
                                       adalias2.key == axis[1], adalias2.measurement == measurement[1]),
                                  TableNumerical.name_id == adalias2.name_id, values)

        sql = select(subquery.c.name_id, func.avg(subquery.c.value1).label(f'{axis[0]}_{measurement[0]}'),
                     func.avg(subquery.c.value2).label(f'{axis[1]}_{measurement[1]}'),
                     func.string_agg(distinct(TableCategorical.value),
                                     literal_column("'<br>'")).label(categorical_entities[0])).\
            join(TableCategorical, TableCategorical.name_id == subquery.c.name_id).\
            where(and_(TableCategorical.key == categorical_entities[0],
                       TableCategorical.value.in_(categorical_entities[1]))).\
            group_by(subquery.c.name_id)

    if limit_filter.get('selected') is not None:
        sql = sql.limit(limit_filter.get('limit')).offset(limit_filter.get('offset'))

    try:
        df = pd.read_sql(sql, r.connection())
        if df.empty:
            df, error = df, "One of the selected entities is empty"
            return df, error
        else:
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"