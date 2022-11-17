from medex.services.filter import FilterService
from modules.models import TableNumerical, TableCategorical
from sqlalchemy.sql import select, distinct
from sqlalchemy.orm import aliased
from sqlalchemy import and_, literal_column, func
import pandas as pd
from modules.filtering import checking_date_filter, apply_limit_to_sql_query


def get_scatter_plot(
            add_group_by, axis, measurement, categorical_entities, date_filter, limit_filter,
            filter_service: FilterService, session_db
):
    adalias2 = aliased(TableNumerical)

    sql_select = select(TableNumerical.name_id, func.avg(TableNumerical.value).label('value1'),
                        func.avg(adalias2.value).label('value2'))
    sql_with_filter = filter_service.apply_filter(TableNumerical, sql_select)
    sql_with_where = sql_with_filter.where(and_(TableNumerical.key == axis[0], 
                                                TableNumerical.measurement == measurement[0], adalias2.key == axis[1], 
                                                adalias2.measurement == measurement[1],
                                                TableNumerical.name_id == adalias2.name_id, 
                                                checking_date_filter(date_filter, TableNumerical))).\
        group_by(TableNumerical.name_id)
    sql_with_group = _add_group_by(add_group_by, axis, categorical_entities, measurement, sql_with_where)

    sql_with_limit = apply_limit_to_sql_query(limit_filter, sql_with_group)
    df = pd.read_sql(sql_with_limit, session_db.connection())
    df.rename(columns={'value1': f'{axis[0]}_{measurement[0]}', 'value2': f'{axis[1]}_{measurement[1]}'}, inplace=True)
    return df, None


def _add_group_by(add_group_by, axis, categorical_entities, measurement, sql_with_where):
    if add_group_by:
        sql_with_group = select(sql_with_where.c.name_id,
                                func.avg(sql_with_where.c.value1).label('value1'),
                                func.avg(sql_with_where.c.value2).label('value2'),
                                func.string_agg(distinct(TableCategorical.value),
                                                literal_column("'<br>'")).label(categorical_entities[0])). \
            join(TableCategorical, TableCategorical.name_id == sql_with_where.c.name_id). \
            where(and_(TableCategorical.key == categorical_entities[0],
                       TableCategorical.value.in_(categorical_entities[1]))). \
            group_by(sql_with_where.c.name_id)
    else:
        sql_with_group = sql_with_where
    return sql_with_group
