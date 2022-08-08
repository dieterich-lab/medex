from modules.models import TableNumerical, TableCategorical, TableDate
from sqlalchemy.sql import union, select
from modules.filtering import checking_date_filter
from sqlalchemy import String, and_, literal_column, asc, text, desc, func, case
from modules.get_data_to_heatmap import apply_filter_heatmap
import pandas as pd


def get_data_print(table_browser, information_from_request, date_filter, update_filter, session_db):
    sql_statement = get_data(table_browser, date_filter, update_filter)
    sql_order_limit = _sort_and_limit(information_from_request, sql_statement)
    df = pd.read_sql(sql_order_limit, session_db.connection())
    return df


def get_data_download(table_browser, date_filter, update_filter, session_db):
    sql_statement = get_data(table_browser, date_filter, update_filter)
    df = pd.read_sql(sql_statement, session_db.connection())
    return df.to_csv()


def get_data(table_browser, date_filter, update_filter):
    sql_union = union(*[select(name.name_id, name.case_id, name.date, name.measurement, name.key,
                        name.value.cast(String).label('value')).
                      where(and_(name.key.in_(table_browser[0]), name.measurement.in_(table_browser[1]),
                                 checking_date_filter(date_filter, name)))

                        for i, name in enumerate([TableCategorical, TableNumerical, TableDate])
                        ])

    sql_statement = _get_what_type_of_table_print(table_browser[0], sql_union, update_filter, table_browser[2])

    return sql_statement


def _get_what_type_of_table_print(entities, sql_union, update_filter, what_table):
    if what_table == 'long':
        sql_select = select(sql_union.c)
    else:
        sql_group_by = select(sql_union.c.name_id, sql_union.c.case_id, sql_union.c.date, sql_union.c.measurement,
                              sql_union.c.key,
                              func.string_agg(sql_union.c.value, literal_column("';'")).label('value')). \
            group_by(sql_union.c.name_id, sql_union.c.case_id, sql_union.c.date, sql_union.c.measurement,
                     sql_union.c.key)

        case_when = [func.min(case([(sql_group_by.c.key == i, sql_group_by.c.value)])).label(i) for i in entities]
        sql_select = select(sql_group_by.c.name_id, sql_group_by.c.case_id, sql_group_by.c.date,
                            sql_group_by.c.measurement, *case_when).\
            group_by(sql_group_by.c.name_id, sql_group_by.c.case_id, sql_group_by.c.date, sql_group_by.c.measurement)

    sql_statement = apply_filter_heatmap(sql_select, update_filter)
    return sql_statement


def _sort_and_limit(information_from_request, sql_statement):
    if information_from_request[3][1] == 'desc':
        sort = desc(text(f'"{information_from_request[3][0]}"'))
    else:
        sort = asc(text(f'"{information_from_request[3][0]}"'))
    sql_order_limit = sql_statement. \
        order_by(sort). \
        limit(information_from_request[1]).offset(information_from_request[2])
    return sql_order_limit


def get_table_size(session_db, table_browser, date_filter, update_filter):
    sql_statement = get_data(table_browser, date_filter, update_filter)
    table_size = select(func.count(sql_statement.c.name_id).label('count'))
    df_table_size = pd.read_sql(table_size, session_db.connection())
    table_size_count = str(df_table_size.iloc[0]['count'])
    return table_size_count