import pandas as pd
import numpy as np
import datetime
from collections import ChainMap
import textwrap as tr


def get_header(r):
    sql = "SELECT * FROM header"
    try:
        df = pd.read_sql(sql, r)
        name_id, measurement_name = df['name_id'][0], df['measurement'][0]
    except (Exception,):
        name_id, measurement_name = 'name_id', 'measurement'
    return name_id, measurement_name


def get_database_information(r):
    size_num_table = """SELECT count(*) FROM examination_numerical"""
    size_date_table = """SELECT count(*) FROM examination_date"""
    size_cat_table = """SELECT count(*) FROM examination_categorical"""
    try:
        size_num_tab, size_date_tab, size_cat_tab = pd.read_sql(size_num_table, r), pd.read_sql(size_date_table, r), \
                                                    pd.read_sql(size_cat_table, r)
        size_num_tab, size_date_tab, size_cat_tab = \
            size_num_tab.iloc[0]['count'], size_date_tab.iloc[0]['count'],\
            size_cat_tab.iloc[0]['count']
                                                    
    except (Exception,):
        size_num_tab, size_date_tab, size_cat_tab = 0, 0, 0
    return size_num_tab, size_date_tab, size_cat_tab
        

def get_date(r):
    sql = """ SELECT min("date"),max("date") FROM examination_numerical """
    try:
        df = pd.read_sql(sql, r)
        start_date = datetime.datetime.strptime(df['min'][0], '%Y-%m-%d').timestamp() * 1000
        end_date = datetime.datetime.strptime(df['max'][0], '%Y-%m-%d').timestamp() * 1000
    except (Exception,):
        now = datetime.datetime.now()
        start_date = datetime.datetime.timestamp(now - datetime.timedelta(days=365.24*100)) * 1000
        end_date = datetime.datetime.timestamp(now) * 1000
    return start_date, end_date


def patient(r):
    sql = """SELECT * FROM Patient"""
    try:
        df = pd.read_sql(sql, r)
        return df['name_id'], None
    except (Exception,):
        return None, "Problem with load data from database"


def get_entities(r):
    all_entities = """SELECT key,type,description,synonym FROM name_type ORDER BY orders """
    try:
        entities = pd.read_sql(all_entities, r)
        entities = entities.replace([None], ' ')
        num_entities = entities[entities['type'] == 'Double'].drop(columns=['type'])
        cat_entities = entities[entities['type'] == 'String'].drop(columns=['type'])
        date_entities = entities[entities['type'] == 'Date'].drop(columns=['type'])
        entities = entities.drop(columns=['type'])

        all_num_entities, all_cat_entities = num_entities.to_dict('index'), cat_entities.to_dict('index')
        all_date_entities, all_entities = date_entities.to_dict('index'), entities.to_dict('index')

        all_num_entities_list, all_cat_entities_list = num_entities['key'].tolist(), cat_entities['key'].tolist()
        all_date_entities_list, all_entities_list = date_entities['key'].tolist(), entities['key'].tolist()
    except (Exception,):
        all_entities, all_entities_list, all_num_entities, all_num_entities_list = {}, [], {}, []
        all_cat_entities, all_date_entities, all_cat_entities_list, all_date_entities_list = {}, {}, [], []
    return \
        all_entities, all_num_entities, all_cat_entities, all_date_entities, all_num_entities_list, \
        all_cat_entities_list, all_date_entities_list, all_entities_list


def min_max_value_numeric_entities(r):
    min_max = """SELECT key,max(value),min(value) FROM examination_numerical GROUP BY key """
    try:
        df_min_max = pd.read_sql(min_max, r)
        df_min_max = df_min_max.set_index('key')
        df_min_max = df_min_max.to_dict('index')
    except (Exception,):
        df_min_max = pd.DataFrame()
        df_min_max = df_min_max.to_dict('index')
    return df_min_max


def get_subcategories_from_categorical_entities(r):
    all_subcategories = """SELECT DISTINCT key,value FROM examination_categorical ORDER by key """
    try:
        subcategories = pd.read_sql(all_subcategories, r)
        entities = subcategories['key'].unique()
        array = []
        df_subcategories = {}
        # create dictionary with categories and subcategories
        for value in entities:
            df = subcategories[subcategories['key'] == value]
            del df['key']
            df_subcategories[value] = list(df['value'])
            array.append(df_subcategories)

        df_subcategories = dict(ChainMap(*array))
    except (Exception,):
        df_subcategories = {}
    return df_subcategories


def get_measurement(r):
    sql = """SELECT DISTINCT measurement:: int FROM examination_numerical ORDER BY measurement """
    try:
        df = pd.read_sql(sql, r)
        df['measurement'] = df['measurement'].astype(str)
        # show all hide measurement selector when was only one measurement for all entities
        if len(df['measurement']) < 2:
            block_measurement = 'none'
        else:
            block_measurement = 'block'
    except (Exception,):
        df = ["No data"]
        block_measurement = 'none'
    return df['measurement'], block_measurement


def create_temp_table_case_id(case_id):
    case_id_all = "$$" + "$$,$$".join(case_id) + "$$"
    create_table = """BEGIN
                        DROP TABLE IF EXISTS temp_table1;
                        CREATE TEMP TABLE IF NOT EXISTS temp_table_case_ids 
                        AS (SELECT name_id FROM patient WHERE case_id in ({0})) """.format(case_id_all)

#class filtering:


def clean_filter(r):
    sql = "DROP TABLE IF EXISTS temp_table_ids"
    sql_drop = "DROP TABLE IF EXISTS temp_table_with_name_ids"


def add_categorical_filter(filter,r):
    cat = cat.replace('<br>', ',')
    cat = "$$" + cat[(cat.find(' is') + 6):].replace(",", "$$,$$") + "$$"

    query = """ SELECT DISTINCT name_id FROM examination_categorical WHERE key = '{}' AND value IN ({}) 
            """.format(categorical[int(update[0]) - 1], cat)
    query2 = """ SELECT DISTINCT name_id,key FROM examination_categorical WHERE key = '{}' AND value IN ({}) 
             """.format(categorical[int(update[0]) - 1], cat)


def add_numerical_filter(filter, r):
    query = """ SELECT DISTINCT name_id FROM examination_numerical WHERE key = '{}' 
                AND value BETWEEN {} AND {}""".format(numerical_filters_name[int(update[1]) - 1],
                                                      from1[int(update[1]) - 1], to1[int(update[1]) - 1])
    query2 = """ SELECT DISTINCT name_id,key FROM examination_numerical WHERE key = '{}' 
                AND value BETWEEN {} AND {} """.format(numerical_filters_name[int(update[1]) - 1],
                                                       from1[int(update[1]) - 1], to1[int(update[1]) - 1])

    
def remove_filter(filter, r):
    query = """ SELECT name_id FROM temp_table_ids WHERE key IN ({}) GROUP BY name_id 
                    HAVING count(name_id) = {} """.format(filters_join, n)
    sql_drop_2 = "DROP TABLE IF EXISTS temp_table_name_ids"
    create_table = """ CREATE TEMP TABLE temp_table_name_ids as ({}) """.format(query)
    update_table = """ DELETE FROM temp_table_ids WHERE key not in ({}) """.format(filters_join)


def get_data(entity, categorical_entities, numerical_entities, date_entities, what_table, measurement, date,
             limit_selected, limit, offset, update, r):

    measurement = "$$" + "$$,$$".join(measurement) + "$$"

    if date[0] == date[1] and date[2] == 0:
        meas_date = ""
    else:
        meas_date = ',"date"'

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    entity_column_n, entity_column_c, entity_column_d = '', '', ''
    sql_n, sql_c, sql_d = "", "", ""
    join_n, join_c, join_d = "", "", ""
    cte_table_n, cte_table_c, cte_table_d = "", "", ""

    if update == '0,0,No':
        filters_en, filters_ec, filters_ed = "", "", ""
    else:
        filters_en = """ inner join temp_table_name_ids as ttni on en.name_id=ttni.name_id """
        filters_ec = """ inner join temp_table_name_ids as ttni on ec.name_id=ttni.name_id """
        filters_ed = """ inner join temp_table_name_ids as ttni on ed.name_id=ttni.name_id """

    if limit_selected:
        limit = """ LIMIT {0} OFFSET {1}""".format(limit, offset)
    else:
        limit = ''

    if date[2] != 0:
        date_value = 'AND "date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql, sql2 = '', ''
    if not limit_selected and what_table == 'long':
        sql = """(SELECT en.name_id,en."case_id" {6},measurement,key,value::text
                         FROM examination_numerical as en
                         {3}
                         WHERE key IN ({0})  
                         AND measurement IN ({1})
                         {2})
                         UNION
                         (SELECT ec.name_id,ec."case_id" {6},measurement,key,value::text
                         FROM examination_categorical as ec
                         {4}
                         WHERE key IN ({0}) 
                         AND measurement IN ({1})
                         {2})
                         UNION
                         (SELECT ed.name_id,ed."case_id" {6},measurement,key,value::text
                         FROM examination_date as ed
                         {5}
                         WHERE key IN ({0}) 
                         AND measurement IN ({1})
                         {2})
                         """.format(entity_final, measurement, date_value, filters_en, filters_ec, filters_ed,
                                    meas_date)
    else:
        if numerical_entities:
            entity_column_n = '"' + '","'.join(numerical_entities) + '",'
            for i, e in enumerate(numerical_entities):
                if limit_selected:
                    sql_part_n = """(SELECT en.name_id,en."case_id" {5},measurement,key,value::text
                                   FROM examination_numerical as en
                                   {4}
                                   WHERE key = $${0}$$  
                                   AND measurement IN ({1})
                                   {2}
                                   {3}) UNION """.format(e, measurement, date_value, limit, filters_en, meas_date)
                    sql_n = sql_n + sql_part_n
                if what_table != 'long':
                    tab = 'a_{}'.format(i)
                    cte_table = """,
                                    {0} as (SELECT en.name_id,en."case_id" {6},measurement,
                                    STRING_AGG(value::text, ';') "{1}"
                                    FROM examination_numerical en
                                    {5}
                                    WHERE key = $${1}$$
                                    AND measurement IN ({2})
                                    {3}
                                    GROUP BY en.name_id,en."case_id" {6},measurement,key
                                    {4})""".format(tab, e, measurement, date_value, limit, filters_en, meas_date)
                    cte_table_n = cte_table_n + cte_table
                    join = """ 
                            FULL OUTER JOIN {0} 
                            USING(name_id,"case_id" {1},measurement) """.format(tab, meas_date)
                    join_n = join_n + join
        if categorical_entities:
            entity_column_c = '"' + '","'.join(categorical_entities) + '",'
            for i, e in enumerate(categorical_entities):
                if limit_selected:
                    sql_part_c = """(SELECT ec.name_id,ec."case_id" {5},measurement,key,value::text
                                    FROM examination_categorical as ec
                                    {4}
                                    WHERE key = $${0}$$  
                                    AND measurement IN ({1}) 
                                    {2}
                                    {3}) UNION """.format(e, measurement, date_value, limit, filters_ec, meas_date)
                    sql_c = sql_c + sql_part_c
                if what_table != 'long':
                    tab = 'a_{}'.format(len(numerical_entities) + i)
                    cte_table = """,
                                    {0} as (SELECT ec.name_id,ec."case_id" {6},measurement,
                                    STRING_AGG(value::text, ';') "{1}"
                                    FROM examination_categorical ec
                                    {5}
                                    WHERE key = $${1}$$
                                    AND measurement IN ({2})
                                    {3}
                                    GROUP BY ec.name_id,ec."case_id" {6},measurement,key
                                    {4})""".format(tab, e, measurement, date_value, limit, filters_ec, meas_date)
                    cte_table_c = cte_table_c + cte_table
                    join = """ 
                                FULL OUTER JOIN {0} 
                                USING(name_id,"case_id" {1},measurement) """.format(tab, meas_date)
                    join_c = join_c + join
        if date_entities:
            entity_column_d = '"' + '","'.join(date_entities) + '",'
            for i, e in enumerate(date_entities):
                if limit_selected:
                    sql_part_d = """(SELECT ed.name_id,ed."case_id" {5},measurement, key,value::text
                                    FROM examination_date as ed 
                                    {4}
                                    WHERE key = $${0}$$  
                                    AND measurement IN ({1}) 
                                    {2}
                                    {3}) UNION """.format(e, measurement, date_value, limit, filters_ed, meas_date)
                    sql_d = sql_d + sql_part_d
                if what_table != 'long':
                    tab = 'a_{}'.format(len(numerical_entities) + len(categorical_entities) + i)
                    cte_table = """,
                                    {0} as (SELECT ed.name_id,ed."case_id" {6},measurement,
                                    STRING_AGG(value::text, ';') "{1}"
                                    FROM examination_date ed
                                    {5}
                                    WHERE key = $${1}$$
                                    AND measurement IN ({2})
                                    {3}
                                    GROUP BY ed.name_id,ed."case_id" {6},measurement,key
                                    {4} )""".format(tab, e, measurement, date_value, limit, filters_ed, meas_date)
                    cte_table_d = cte_table_d + cte_table
                    join = """
                            FULL OUTER JOIN {0} 
                            USING(name_id,"case_id" {1},measurement) """.format(tab, meas_date)
                    join_c = join_c + join
        if what_table != 'long':
            sql2_part1 = "WITH" + cte_table_n + cte_table_c + cte_table_d + """ SELECT name_id,"case_id" {},
            measurement, """.format(meas_date) + \
                       entity_column_n + entity_column_c + entity_column_d
            sql2_part2 = " From a_0" + join_n + join_c + join_d
            sql2 = sql2_part1[:-1]+sql2_part2
            start = sql2.find(',')
            start_full = sql2.find('FULL')

            sql2 = sql2[0:start] + sql2[start+1:start_full] + sql2[start_full+97::]
        else:
            sql = sql_n + sql_c + sql_d
            sql = sql[:-6]

    try:
        if what_table == 'long':
            df = pd.read_sql(sql, r)
        else:
            df = pd.read_sql(sql2, r)
        return df, None
    except (Exception,):
        df = pd.DataFrame()
        return df, "Problem with load data from database"


def get_basic_stats(entity, measurement, date, limit_selected, limit, offset, update, r):
    """
    param:
     entity: numerical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """

    n = """SELECT COUNT ( DISTINCT name_id) FROM Patient"""
    n = pd.read_sql(n, r)
    n = n['count']

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update == '0,0,No':
        filters = ''
    else:
        filters = """ inner join temp_table_name_ids as ttni on en.name_id=ttni.name_id """
    if date[2] != 0:
        date_value = 'AND "date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql = """ WITH basic_stats as (SELECT en.name_id,key,measurement,AVG(value) as value 
                                   FROM examination_numerical en 
                                   {3}
                                   WHERE key IN ({0})
                                   AND measurement IN ({1}) 
                                   {2}
                                   GROUP BY en.name_id,key,measurement)
                SELECT key,measurement,
                                count(name_id),
                                min(value),
                                max(value),
                                AVG(value) AS "mean",
                                stddev(value),
                                (stddev(value)/sqrt(count(value))) AS "stderr",
                                (percentile_disc(0.5) within group (order by value)) AS median 
                                FROM basic_stats
                                GROUP BY key,measurement 
                                ORDER BY key,measurement
                                """.format(
                                entity_final, measurement, date_value, filters)
    if limit_selected:
        sql_part = ""
        for e in entity:
            s = """ (SELECT key,measurement,en.name_id, AVG(value) as value
                    FROM examination_numerical as en  
                    {3}
                    WHERE key = $${0}$$ 
                    AND measurement IN ({1}) 
                    {2}
                    GROUP BY en.name_id,key,measurement
                    LIMIT {4} OFFSET {5})
                    UNION """.format(e, measurement, date_value, filters, limit, offset)
            sql_part = sql_part + s
        sql_part = sql_part[:-6]
        sql = """ WITH basic_stats AS ({})
                    SELECT key,measurement,
                                    count(name_id),
                                    min(value),
                                    max(value),
                                    AVG(value) AS "mean",
                                    stddev(value),
                                    (stddev(value)/sqrt(count(value))) AS "stderr",
                                    (percentile_disc(0.5) within group (order by value)) AS median 
                                    FROM basic_stats as en  
                                    GROUP BY key,measurement 
                                    ORDER BY key,measurement """.format(sql_part)

    try:
        df = pd.read_sql(sql, r)
        df['count NaN'] = int(n) - df['count']
        df = df.round(2)
        return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_cat_basic_stats(entity, measurement, date, limit_selected, limit, offset, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update == '0,0,No':
        filters = ''
    else:
        filters = """ inner join temp_table_name_ids as ttni on ec.name_id= ttni.name_id """
    if date[2] != 0:
        date_value = 'AND "date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql = """WITH basic_stats as (SELECT ec.name_id,key,measurement
                                   FROM examination_categorical as ec
                                   {3}
                                   WHERE key IN ({0})
                                   AND measurement IN ({1}) 
                                   {2}
                                   GROUP BY ec.name_id,key,measurement)
            SELECT key,measurement,count(name_id) 
                        FROM basic_stats
                        GROUP BY measurement,key """.format(entity_final, measurement, date_value, filters)
    if limit_selected:
        sql_part = ""
        for e in entity:
            s = """ (SELECT key,measurement,ec.name_id
                    FROM examination_categorical as ec 
                    {3}
                    WHERE key = $${0}$$ 
                    AND measurement IN ({1}) 
                    {2}
                    GROUP BY ec.name_id,key,measurement
                    LIMIT {4} OFFSET {5})
                    UNION """.format(e, measurement, date_value, filters, limit, offset)
            sql_part = sql_part + s
        sql_part = sql_part[:-6]
        sql = """ WITH basic_stats AS ({})
                    SELECT key,measurement,count(name_id) 
                        FROM basic_stats
                        GROUP BY measurement,key """.format(sql_part)
    try:
        n = """SELECT COUNT ( DISTINCT name_id) FROM Patient"""
        n = pd.read_sql(n, r)
        n = n['count']
        df = pd.read_sql(sql, r)
        df['count NaN'] = int(n) - df['count']
        return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_date_basic_stats(entity, measurement, date, limit_selected, limit, offset, update, r):
    """
    param:
     entity: date entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """

    n = """SELECT COUNT ( DISTINCT name_id) FROM Patient"""
    n = pd.read_sql(n, r)
    n = n['count']

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update == '0,0,No':
        filters = ''
    else:
        filters = """ inner join temp_table_name_ids as ttni on ed.name_id=ttni.name_id """
    if date[2] != 0:
        date_value = 'AND "date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql = """WITH basic_stats as (SELECT ed.name_id,key,measurement
                                   FROM examination_date as ed
                                   {3}
                                   WHERE key IN ({0})
                                   AND measurement IN ({1}) 
                                   {2}
                                   GROUP BY ed.name_id,key,measurement)
            SELECT key,measurement,count(name_id) 
                        FROM basic_stats
                        GROUP BY measurement,key """.format(entity_final, measurement, date_value, filters)
    if limit_selected:
        sql_part = ""
        for e in entity:
            s = """ (SELECT key,measurement,ed.name_id
                    FROM examination_date as ed 
                    {3}
                    WHERE key = $${0}$$ 
                    AND measurement IN ({1}) 
                    {2}
                    GROUP BY ed.name_id,key,measurement
                    LIMIT {4} OFFSET {5})
                    UNION """.format(e, measurement, date_value, filters, limit, offset)
            sql_part = sql_part + s
        sql_part = sql_part[:-6]
        sql = """ WITH basic_stats AS ({})
                    SELECT key,measurement,count(name_id) 
                        FROM basic_stats
                        GROUP BY measurement,key """.format(sql_part)
    try:
        df = pd.read_sql(sql, r)
        df['count NaN'] = int(n) - df['count']
        return df, None
    except (Exception,):
        return None, "Problem with load data from database"


# I have to work on this
def get_unit(name, r):
    """ Get number of all patients

     number use only for basic_stats
     """
    try:
        sql = """SELECT key,"unit" FROM name_type WHERE key='{}' """.format(name)
        df = pd.read_sql(sql, r)
        return df['unit'][0], None
    except (Exception,):
        return None, "Problem with load data from database"


def get_scatter_plot(add_group_by, entity, subcategory, x_entity, y_entity, x_measurement, y_measurement, date,
                     limit_selected, limit, offset, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """
    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    if update == '0,0,No':
        filters = ''
    else:
        filters = """ inner join temp_table_name_ids as ttni on x.name_id=ttni.name_id """
    if limit_selected:
        limit_selected = """ LIMIT {} OFFSET {} """.format(limit, offset)
    else:
        limit_selected = ''
    if date[2] != 0:
        date_value1 = 'AND x."date" BETWEEN $${0}$$ AND $${1}$$ '.format(date[0], date[1])
        date_value2 = 'AND y."date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value1 = ''
        date_value2 = ''
    if not add_group_by:
        sql = """SELECT x.name_id,AVG(x.value) as "{2}_{0}",AVG(y.value) as "{3}_{1}"
                            FROM examination_numerical as x
                            {6}
                            INNER JOIN examination_numerical as y
                                ON x.name_id = y.name_id
                            WHERE x.key IN ('{0}') 
                            AND y.key IN ('{1}') 
                            AND x.measurement='{2}' 
                            AND y.measurement='{3}' 
                            {4}
                            {5}
                            GROUP BY x.name_id,y.name_id
                            {7}""".format(x_entity, y_entity, x_measurement, y_measurement, date_value1, date_value2,
                                          filters, limit_selected)
    else:
        sql = """SELECT * FROM (SELECT x.name_id,AVG(x.value) as "{2}_{0}",AVG(y.value) as "{3}_{1}",
        STRING_AGG(distinct ec.value,'<br>') as "{6}" 
                            FROM examination_numerical as x
                            {8}
                            INNER JOIN examination_numerical as y
                                ON x.name_id = y.name_id
                            LEFT JOIN examination_categorical as ec
                                ON x.name_id = ec.name_id
                            WHERE x.key IN ('{0}') 
                            AND y.key IN ('{1}') 
                            AND ec.key IN ('{6}')
                            AND x.measurement='{2}' 
                            AND y.measurement='{3}' 
                            {4}
                            {5}
                            GROUP BY x.name_id
                            {9}) foo
                            WHERE foo."{6}" IN ({7})
                            """.format(x_entity, y_entity, x_measurement, y_measurement, date_value1, date_value2,
                                       entity, subcategory, filters, limit_selected)

    try:
        df = pd.read_sql(sql, r)
        x_axis_m = x_entity + '_' + x_measurement
        y_axis_m = y_entity + '_' + y_measurement
        if not add_group_by:
            df.columns = ['name_id', x_axis_m, y_axis_m]
        else:
            df.columns = ['name_id', x_axis_m, y_axis_m, entity]
        if df.empty:
            df, error = df, "One of the selected entities is empty"
            return df, error
        else:
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_bar_chart(entity, subcategory, measurement, date, limit_selected, limit, offset, update, r):

    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update == '0,0,No':
        filters = ''
    else:
        filters = """ inner join temp_table_name_ids as ttni on ec.name_id=ttni.name_id """
    if limit_selected:
        limit_selected = """ LIMIT {} OFFSET {} """.format(limit, offset)
    else:
        limit_selected = ''
    if date[2] != 0:
        date_value = 'AND "date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql = """SELECT value AS "{0}",measurement,count(value)
                FROM (SELECT STRING_AGG(distinct value,'<br>')  AS value,measurement FROM examination_categorical 
                as ec
                        {4} 
                        WHERE key='{0}'
                        AND value IN ({1}) 
                        {3}
                        AND measurement IN ({2})
                        GROUP BY ec.name_id,measurement
                        {5}) AS foo
                GROUP BY value,measurement
                """.format(entity, subcategory, measurement, date_value, filters, limit_selected)
    try:
        df = pd.read_sql(sql, r)
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            df.columns = [entity, 'measurement', 'count']
            df[entity] = df[entity].str.wrap(30).replace(to_replace=[r"\\n", "\n"],
                                                         value=["<br>", "<br>"], regex=True)
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_histogram_box_plot(entity_num, entity_cat, subcategory, measurement, date, limit_selected, limit, offset,
                           update, r):

    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update == '0,0,No':
        filters = ''
    else:
        filters = """ inner join temp_table_name_ids as ttni on en.name_id=ttni.name_id """
    if limit_selected:
        limit_selected = """ LIMIT {} OFFSET {} """.format(limit, offset)
    else:
        limit_selected = ''
    if date[2] != 0:
        date_value = 'AND en."date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql = """SELECT en.name_id,en.measurement,AVG(en.value) AS "{0}",ec.value AS "{1}"
                FROM examination_numerical AS en 
                {5}
                LEFT JOIN examination_categorical AS ec 
                ON en.name_id = ec.name_id
                WHERE en.key = '{0}' 
                AND ec.key = '{1}' 
                AND ec.value IN ({2}) 
                AND en.measurement IN ({3}) 
                {4}
                GROUP BY en.name_id,en.measurement,ec.value
                {6}
                """.format(entity_num, entity_cat, subcategory, measurement, date_value, filters, limit_selected)
    try:
        df = pd.read_sql(sql, r)
        if df.empty or len(df) == 0:
            return df, "The entity {0} or {1} wasn't measured".format(entity_num, entity_cat)
        else:
            df.columns = ["name", 'measurement', entity_num, entity_cat]
            df[entity_cat] = df[entity_cat].str.wrap(30).replace(to_replace=[r"\\n", "\n"], value=["<br>", "<br>"],
                                                                 regex=True)
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_heat_map(entity, date, limit_selected, limit, offset, update, r):

    case_statement = ""
    crosstab_columns = ""
    if update == '0,0,No':
        filters = ''
    else:
        filters = """ inner join temp_table_name_ids as ttni on en.name_id=ttni.name_id """
    for ent in entity:
        create_case_statement = """case WHEN key = '{0}' THEN value END AS "{0}" """.format(ent)
        case_statement = case_statement + ',' + create_case_statement
        create_crosstab_columns = '"{}" double precision'.format(ent)
        crosstab_columns = crosstab_columns + ',' + create_crosstab_columns
    if date[2] != 0:
        date_value = 'AND en."date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    sql = """SELECT en.name_id,key,AVG(value) as value 
                FROM examination_numerical as en
                {2} 
                WHERE key IN ({0}) 
                {1}
                GROUP BY en.name_id,key """.format(entity_fin, date_value, filters)

    if limit_selected:
        sql = ""
        for e in entity:
            sql_part = """(SELECT en.name_id,key,value 
                           FROM examination_numerical as en 
                           {2}
                           WHERE key = $${0}$$  
                           {1}
                           LIMIT {3} 
                           OFFSET {4}) UNION """.format(e, date_value, filters, limit, offset)
            sql = sql + sql_part
        sql = """ SELECT name_id,key,AVG(value) as value FROM (""" + sql[:-6] + """) 
        foo GROUP BY name_id,key """

    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=['name_id'], columns='key', values='value', aggfunc=np.mean).reset_index()
        new_columns = [tr.fill(x, width=20).replace("\n", "<br>") for x in df.columns.values]
        df.columns = new_columns
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def calculator(entity1, entity2, date_first_measurement, date_second_measurement, column_name, r):

    sql = """ SELECT a.name_id,a."date",date_PART('year',a.value::timestamp) - 
    date_PART('year',b.value::timestamp) as {4}
    FROM (SELECT name_id,"date",measurement,value 
    from examination_date WHERE key='{0}' and measurement='{2}' 
    group by name_id,"date",measurement,value) as a 
    LEFT JOIN (SELECT name_id,measurement,value from examination_date WHERE key='{1}' 
    and measurement='{3}' group by name_id,measurement,value) as b 
    ON a.name_id = b.name_id """.format(entity1, entity2, date_first_measurement, date_second_measurement, column_name)

    try:
        df = pd.read_sql(sql, r)
        df = df.dropna()
        df.reset_index(drop=True, inplace=True)
        df.sort_index(inplace=True)
        return df
    except (Exception,):
        return None


""" 
def push_to_numerical_table(column_name, df, r):

    sql_order = " select orders from name_type order by orders desc limit 1 "
    sql_id = " select "id" from examination_numerical order by "id" desc limit 1 "

    try:
        # df_order = pd.read_sql(sql_order, r)
        # order = df_order['order'][0] + 1
        # row = [order, column_name, 'Double']

        output = io.StringIO()
        df_id = pd.read_sql(sql_id, r)
        ids = df_id['id'][0] + 1
        df["id"] = df["id"] + ids
        df.to_csv(output, sep=',', header=False, index=False)
        output.seek(0)
        r.commit()
    except (Exception,):
        print('Problem')
"""