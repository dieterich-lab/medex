from sqlalchemy.sql import join
from sqlalchemy import text
import pandas as pd


def clean_filter(r):
    sql = "DROP TABLE IF EXISTS temp_table_ids"
    sql_drop = "DROP TABLE IF EXISTS temp_table_name_ids"

    r.execute(sql)
    r.execute(sql_drop)


def first_filter(query, query2, r):
    create_table = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_name_ids as ({}) """.format(query)
    create_table_2 = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_ids as ({}) """.format(query2)

    r.execute(create_table)
    r.execute(create_table_2)


def next_filter(query, query2, r):
    create_table = """ DELETE FROM temp_table_name_ids WHERE name_id NOT IN ({})""".format(query)
    create_table_2 = """ INSERT INTO temp_table_ids ({}) """.format(query2)

    r.execute(create_table)
    r.execute(create_table_2)


def add_categorical_filter(filters, n, r):
    subcategory = "$$" + "$$,$$".join(filters[2].get('sub')) + '$$'

    query = F"""SELECT DISTINCT ec.name_id FROM examination_categorical ec 
                WHERE ec.key = '{filters[1].get('cat')}' AND ec.value IN ({subcategory}) 
                AND ec.measurement = '{filters[0].get('measurement')}'"""
    query2 = F"""SELECT DISTINCT ec.name_id,ec.key,ec.measurement FROM examination_categorical ec 
                 WHERE ec.key = '{filters[1].get('cat')}' AND ec.value IN ({subcategory}) 
                 AND ec.measurement = '{filters[0].get('measurement')}'"""
    if n == 1:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def add_numerical_filter(filters, n, r):
    from_to = filters[2].get('from_to').split(";")
    query = F"""SELECT DISTINCT en.name_id FROM examination_numerical en 
                WHERE en.key = '{filters[1].get('num')}'  AND en.value BETWEEN {from_to[0]} AND {from_to[1]} 
                AND en.measurement = '{filters[0].get('measurement')}'"""
    query2 = F"""SELECT DISTINCT en.name_id,en.key,en.measurement FROM examination_numerical en 
                WHERE key = '{filters[1].get('num')}' AND en.value BETWEEN {from_to[0]} AND {from_to[1]} 
                AND en.measurement = '{filters[0].get('measurement')}'"""

    if n == 1:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def add_case_ids_to_filter(case_id, n, check_case_id, r):

    case_id_all = "$$" + "$$,$$".join(case_id) + "$$"

    create_temp_table_case_id(case_id_all, r)

    query = """ SELECT DISTINCT name_id FROM patient WHERE case_id in ({0}) """.format(case_id_all)
    query2 = """ SELECT name_id,(CASE WHEN case_id !='' THEN 'case_id' END) as key FROM patient 
    WHERE case_id in ({0}) """.format(case_id_all)
    if check_case_id == 'Yes' and n == 1:
        clean_filter(r)
    elif check_case_id == 'Yes' and n != 1:
        remove_one_filter('case_id', n, r)

    if n == 1:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def create_temp_table_case_id(case_id_all, r):
    sql_drop = "DROP TABLE IF EXISTS temp_table_case_ids"
    create_table = """ CREATE TEMP TABLE temp_table_case_ids as (SELECT DISTINCT case_id FROM patient where 
    case_id in ({0})) """.format(case_id_all)
    r.execute(sql_drop)
    r.execute(create_table)


def get_case_ids(r):
    sql = text("SELECT * FROM temp_table_case_ids")
    df = pd.read_sql(sql, r.connection())
    return df.to_csv()


def remove_one_filter(filters, filter_update, r):
    filter_list = filters.split(";")
    update_table = F""" DELETE FROM temp_table_ids WHERE key = '{filter_list[1]}' 
AND measurement = '{filter_list[0]}' """
    sql_drop = "DROP TABLE IF EXISTS temp_table_name_ids"

    query = """ SELECT name_id FROM temp_table_ids 
                    GROUP BY name_id 
                    HAVING count(name_id) = {} """.format(filter_update)
    create_table = """ CREATE TEMP TABLE temp_table_name_ids as ({}) """.format(query)

    r.execute(update_table)
    r.execute(sql_drop)
    r.execute(create_table)


def checking_date_filter(date_filter, table):
    if date_filter[2] != 0:
        values = table.date.between(date_filter[3], date_filter[4])
    else:
        values = text('')

    return values


def apply_filter_to_sql(update_filter, table, sql):
    if update_filter['filter_update'] != '0':
        j = join(table, text("temp_table_name_ids"),
                 table.name_id == text("temp_table_name_ids.name_id"))
        sql = sql.select_from(j)
    else:
        sql = sql
    return sql


def apply_limit_to_sql_query(limit_filter, sql):
    if limit_filter.get('selected') is not None:
        sql = sql.limit(limit_filter['limit']).offset(limit_filter['offset'])
    else:
        sql = sql
    return sql
