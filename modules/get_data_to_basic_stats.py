from modules.models import TableNumerical, TableCategorical, TableDate, Patient
from sqlalchemy.sql import union, select, distinct, label
from sqlalchemy import and_, func
import pandas as pd
from modules.filtering import checking_date_filter,checking_filter


def get_basic_stats(entity, measurement, date_filter, limit_filter, update_filter, r):
    n = select(func.count(distinct(Patient.name_id)).label('count'))
    s22 = []
    values = checking_date_filter(date_filter, TableNumerical)
    s2 = select(TableNumerical.key, TableNumerical.measurement, TableNumerical.name_id,
                func.avg(TableNumerical.value).label('value'))
    if limit_filter.get('selected') is not None:
        for e in entity:
            s2 = checking_filter(update_filter, TableNumerical, s2)
            s22.append(s2.where(and_(TableNumerical.key == e, TableNumerical.measurement.in_(measurement), values)).
                       group_by(TableNumerical.name_id, TableNumerical.key, TableNumerical.measurement).
                       limit(limit_filter.get('limit')).offset(limit_filter.get('offset')))
        sql_part2 = union(*s22)
    else:
        s2 = checking_filter(update_filter, TableNumerical, s2)
        sql_part2 = s2.where(and_(TableNumerical.key.in_(entity), TableNumerical.measurement.in_(measurement),
                                  values)).\
            group_by(TableNumerical.name_id, TableNumerical.key, TableNumerical.measurement)

    sql_part2 = sql_part2.cte('distinct_query')
    sql = select(sql_part2.c.key, sql_part2.c.measurement,
                 func.count(sql_part2.c.name_id).label('count'), func.min(sql_part2.c.value).label('min'),
                 func.max(sql_part2.c.value).label('max'),
                 func.avg(sql_part2.c.value).label('mean'),
                 func.stddev(sql_part2.c.value).label('stddev'),
                 label('stderr', func.stddev(sql_part2.c.value).label('stddev')/func.sqrt(func.count(sql_part2.c.value))
                       ),
                 func.percentile_cont(0.5).within_group(sql_part2.c.value).label('median')).\
        group_by(sql_part2.c.key, sql_part2.c.measurement).\
        order_by(sql_part2.c.key, sql_part2.c.measurement)

    try:
        df = pd.read_sql(sql, r.connection())
        n = pd.read_sql(n, r.connection())
        n = n['count']
        df['count NaN'] = int(n) - df['count']
        df = df.round(2)

        return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_cat_date_basic_stats(entity, measurement, date_filter, limit_filter, update_filter, table, r):
    if table == 'examination_categorical':
        name = TableCategorical
    else:
        name = TableDate
    n = select(func.count(distinct(Patient.name_id)).label('count'))
    s22 = []

    values = checking_date_filter(date_filter, name)
    s2 = select(name.key, name.measurement, name.name_id)
    if limit_filter.get('selected') is not None:
        for e in entity:
            s2 = checking_filter(update_filter, name, s2)
            s22.append(s2.where(and_(name.key == e, name.measurement.in_(measurement), values)).
                       group_by(name.name_id, name.key, name.measurement).
                       limit(limit_filter.get('limit')).offset(limit_filter.get('offset')))
        sql_part2 = union(*s22)
    else:
        s2 = checking_filter(update_filter, name, s2)
        sql_part2 = s2.where(and_(name.key.in_(entity), name.measurement.in_(measurement), values)). \
            group_by(name.name_id, name.key, name.measurement)

    sql_part2 = sql_part2.cte('distinct_query')
    sql = select(sql_part2.c.key, sql_part2.c.measurement, func.count(sql_part2.c.name_id).label('count')).\
        group_by(sql_part2.c.key, sql_part2.c.measurement).\
        order_by(sql_part2.c.key, sql_part2.c.measurement)

    try:
        n = pd.read_sql(n, r.connection())
        n = n['count']
        df = pd.read_sql(sql, r.connection())
        df['count NaN'] = int(n) - df['count']
        return df, None
    except (Exception,):
        return None, "Problem with load data from database"