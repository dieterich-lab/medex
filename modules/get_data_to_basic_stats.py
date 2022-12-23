from typing import List

from medex.services.database import get_db_engine
from medex.services.filter import FilterService
from modules.models import TableNumerical, TableCategorical, TableDate, Patient
from sqlalchemy.sql import union, select, distinct, label
from sqlalchemy import and_, func
import pandas as pd
from modules.filtering import checking_date_filter


def get_num_basic_stats(
        entities: List[str], measurement: List[str], date_filter, limit_filter, filter_service: FilterService
):
    select_numerical_values_sql = select(
        TableNumerical.key, TableNumerical.measurement, TableNumerical.name_id,
        func.avg(TableNumerical.value).label('value')
    )
    select_numerical_values_with_filter_sql = filter_service.apply_filter(TableNumerical, select_numerical_values_sql)
    raw_data_sql = _get_raw_data_sql(entities, limit_filter, measurement, select_numerical_values_with_filter_sql,
                                     checking_date_filter(date_filter, TableNumerical))
    with_raw_data = raw_data_sql.cte('raw_data')
    sql = select(
        with_raw_data.c.key, with_raw_data.c.measurement,
        func.count(with_raw_data.c.name_id).label('count'),
        func.min(with_raw_data.c.value).label('min'),
        func.max(with_raw_data.c.value).label('max'),
        func.avg(with_raw_data.c.value).label('mean'),
        func.stddev(with_raw_data.c.value).label('stddev'),
        label(
            'stderr', func.stddev(with_raw_data.c.value).label('stddev')/func.sqrt(func.count(with_raw_data.c.value))
        ),
        func.percentile_cont(0.5).within_group(with_raw_data.c.value).label('median')
    ).\
        group_by(with_raw_data.c.key, with_raw_data.c.measurement).\
        order_by(with_raw_data.c.key, with_raw_data.c.measurement)
    df = pd.read_sql(sql, get_db_engine())
    n = _get_patient_count()
    df['count NaN'] = n - df['count']
    df = df.round(2)
    return df, None


def _get_patient_count():
    patient_count_sql = select(func.count(distinct(Patient.name_id)).label('count'))
    patient_count_result = pd.read_sql(patient_count_sql, get_db_engine())
    return int(patient_count_result['count'])


def _get_raw_data_sql(entities, limit_filter, measurement, select_numerical_values_with_filter_sql, values):
    if limit_filter.get('selected') is not None:
        return union(*[
            select_numerical_values_with_filter_sql.where(
                and_(TableNumerical.key == e, TableNumerical.measurement.in_(measurement), values)).
            group_by(TableNumerical.name_id, TableNumerical.key, TableNumerical.measurement).
            limit(limit_filter.get('limit')).offset(limit_filter.get('offset'))

            for e in entities
        ])
    else:
        return select_numerical_values_with_filter_sql.where(
            and_(TableNumerical.key.in_(entities), TableNumerical.measurement.in_(measurement),
                 values)). \
            group_by(TableNumerical.name_id, TableNumerical.key, TableNumerical.measurement)


def get_cat_date_basic_stats(entities, measurement, date_filter, limit_filter, filter_service: FilterService,
                             table, db_session):
    if table == 'examination_categorical':
        name = TableCategorical
    else:
        name = TableDate

    values = checking_date_filter(date_filter, name)
    select_values_sql = select(name.key, name.measurement, name.name_id)
    select_numerical_values_with_filter_sql = filter_service.apply_filter(name, select_values_sql)

    if limit_filter.get('selected') is not None:
        raw_data = union(*[select_numerical_values_with_filter_sql.
                         where(and_(name.key == e, name.measurement.in_(measurement), values)).
                         group_by(name.name_id, name.key, name.measurement).
                         limit(limit_filter.get('limit')).offset(limit_filter.get('offset'))

                         for e in entities
                           ])
    else:
        raw_data = select_numerical_values_with_filter_sql.\
            where(and_(name.key.in_(entities), name.measurement.in_(measurement), values)). \
            group_by(name.name_id, name.key, name.measurement)

    with_raw_data = raw_data.cte('raw_data')
    sql = select(with_raw_data.c.key, with_raw_data.c.measurement, func.count(with_raw_data.c.name_id).label('count')).\
        group_by(with_raw_data.c.key, with_raw_data.c.measurement).\
        order_by(with_raw_data.c.key, with_raw_data.c.measurement)

    n = _get_patient_count()
    df = pd.read_sql(sql, db_session.connection())
    df['count NaN'] = n - df['count']
    return df, None
