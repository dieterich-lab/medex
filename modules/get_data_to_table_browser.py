from modules.models import TableNumerical, TableCategorical, TableDate
from sqlalchemy.sql import union, select
from modules.filtering import checking_date_filter
from sqlalchemy import String, and_, literal_column, asc, text, desc, func
from modules.get_data_to_heatmap import case_when_for_sql_statement
import pandas as pd


def get_data_print(entities, what_table, measurement, limit, offset, sort, date_filter, update_filter, session_db):
    sql_statement = get_data(entities, what_table, measurement, date_filter, update_filter)
    sql_order_limit = _sort_and_limit(limit, offset, sort, sql_statement)
    df = pd.read_sql(sql_order_limit, session_db.connection())
    table_size_count = get_table_size(session_db, sql_statement)
    return df, table_size_count, None


def get_data_download(entities, what_table, measurement, date_filter, update_filter, session_db):
    sql_statement = get_data(entities, what_table, measurement, date_filter, update_filter)
    df = pd.read_sql(sql_statement, session_db.connection())
    return df.to_csv()


def get_data(entities, what_table, measurement, date_filter, update_filter):
    sql_union = union(*[select(name.name_id, name.case_id, name.date, name.measurement, name.key,
                        name.value.cast(String).label('value')).
                      where(and_(name.key.in_(entities), name.measurement.in_(measurement),
                                 checking_date_filter(date_filter, name)))

                        for i, name in enumerate([TableCategorical, TableNumerical, TableDate])
                        ])

    sql_statement = _get_what_type_of_table_print(entities, sql_union, update_filter, what_table)

    return sql_statement


def _get_what_type_of_table_print(entities, sql_union, update_filter, what_table):
    if what_table == 'long':
        sql_select = select(sql_union.c)
        sql_statement = _apply_filter_table_browser_sql(sql_select, update_filter, sql_union)

    else:
        sql_group_by = select(sql_union.c.name_id, sql_union.c.case_id, sql_union.c.date, sql_union.c.measurement,
                              sql_union.c.key,
                              func.string_agg(sql_union.c.value, literal_column("';'")).label('value')). \
            group_by(sql_union.c.name_id, sql_union.c.case_id, sql_union.c.date, sql_union.c.measurement,
                     sql_union.c.key)

        case_when = case_when_for_sql_statement(entities)
        sql_select = select(sql_group_by.c.name_id, sql_group_by.c.case_id, sql_group_by.c.date,
                            sql_group_by.c.measurement, text(case_when))
        sql_statement = _apply_filter_table_browser_sql(sql_select, update_filter, sql_group_by)

        sql_statement = sql_statement.group_by(sql_group_by.c.name_id, sql_group_by.c.case_id,
                                               sql_group_by.c.date, sql_group_by.c.measurement)
    return sql_statement


def _apply_filter_table_browser_sql(sql_select, update_filter, sql_union):
    if update_filter['filter_update'] != 0:
        sql_statement = sql_select. \
            join(text('temp_table_name_ids'), sql_union.c.name_id == text('temp_table_name_ids.name_id'))
    else:
        sql_statement = sql_select
    return sql_statement


def _sort_and_limit(limit, offset, sort, sql_statement):
    if sort[1] == 'desc':
        sort = desc(text(f'"{sort[0]}"'))
    else:
        sort = asc(text(f'"{sort[0]}"'))
    sql_order_limit = sql_statement. \
        order_by(sort). \
        limit(limit).offset(offset)
    return sql_order_limit


def get_table_size(r, sql_statement):
    table_size = select(func.count(sql_statement.c.name_id).label('count'))
    print(table_size)
    df_table_size = pd.read_sql(table_size, r.connection())
    table_size_count = df_table_size.iloc[0]['count']
    return table_size_count
