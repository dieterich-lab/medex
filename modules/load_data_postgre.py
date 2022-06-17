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


def create_temp_table_case_id(case_id, r):
    case_id_all = "$$" + "$$,$$".join(case_id) + "$$"
    create_table = """BEGIN DROP TABLE IF EXISTS temp_table1;
                        CREATE TEMP TABLE IF NOT EXISTS temp_table_case_ids 
                        AS (SELECT name_id FROM patient WHERE case_id in ({0})) """.format(case_id_all)

    r.execute(create_table)


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
    subcategory = "$$" + "$$,$$".join(filters[1].get('sub')) + '$$'

    query = """SELECT DISTINCT name_id FROM examination_categorical WHERE key = '{}' AND value IN ({}) 
    """.format(filters[0].get('cat'), subcategory)
    query2 = """SELECT DISTINCT name_id,key FROM examination_categorical WHERE key = '{}' AND value IN ({}) 
    """.format(filters[0].get('cat'), subcategory)

    if n == 0:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def add_numerical_filter(filters, n, r):
    from_to = filters[1].get('from_to').split(";")
    query = """ SELECT DISTINCT name_id FROM examination_numerical WHERE key = '{}' 
                AND value BETWEEN {} AND {}""".format(filters[0].get('num'), from_to[0], from_to[1])
    query2 = """ SELECT DISTINCT name_id,key FROM examination_numerical WHERE key = '{}' 
                AND value BETWEEN {} AND {} """.format(filters[0].get('num'), from_to[0], from_to[1])

    if n == 0:
        first_filter(query, query2, r)
    else:
        next_filter(query, query2, r)


def remove_one_filter(filters, filter_update, r):
    update_table = """ DELETE FROM temp_table_ids WHERE key = '{}' """.format(filters)
    sql_drop = "DROP TABLE IF EXISTS temp_table_name_ids"

    query = """ SELECT name_id FROM temp_table_ids 
                    GROUP BY name_id 
                    HAVING count(name_id) = {1} """.format(filters, filter_update)
    create_table = """ CREATE TEMP TABLE temp_table_name_ids as ({}) """.format(query)

    r.execute(update_table)
    r.execute(sql_drop)
    r.execute(create_table)


def checking_for_filters(date_filter, limit_filter, update_filter):

    if update_filter == 0:
        filters = ''
    else:
        filters = """ inner join temp_table_name_ids as ttni on foo.name_id=ttni.name_id """

    if limit_filter.get('selected'):
        limit_selected = """ LIMIT {} OFFSET {} """.format(limit_filter.get('limit'), limit_filter.get('offset'))
    else:
        limit_selected = ''

    if date_filter[2] != 0:
        date_value1 = 'AND x."date" BETWEEN $${0}$$ AND $${1}$$ '.format(date_filter[0], date_filter[1])
        date_value2 = 'AND y."date" BETWEEN $${0}$$ AND $${1}$$'.format(date_filter[0], date_filter[1])
        date_value = 'AND "date" BETWEEN $${0}$$ AND $${1}$$'.format(date_filter[0], date_filter[1])
    else:
        date_value1 = ''
        date_value2 = ''
        date_value = ''

    return filters, limit_selected, date_value1, date_value2, date_value


def get_data(entities, what_table, measurement, limit, offset, update_filter, r):
    measurement = "$$" + "$$,$$".join(measurement) + "$$"
    entity_final = "$$" + "$$,$$".join(entities) + "$$"

    if update_filter == 0:
        filters = ''
    else:
        filters = """ inner join temp_table_name_ids as ttni on foo.name_id=ttni.name_id """

    select_union = """SELECT name_id,case_id,measurement,key,value::text FROM examination_numerical 
                                    WHERE key IN ({0}) AND measurement IN ({1})
                                    UNION 
                                SELECT name_id,case_id,measurement,key,value FROM examination_categorical 
                                    WHERE key IN ({0}) AND measurement IN ({1})
                                    UNION
                                SELECT name_id,case_id,measurement,key,value::text FROM examination_date 
                                    WHERE key IN ({0}) AND measurement IN ({1})""".format(entity_final, measurement)

    if what_table == 'long':
        sql = """ SELECT foo.name_id,foo.case_id,foo.measurement,foo.key,foo.value::text FROM ({0}) foo
                         {3}
                            ORDER BY foo.name_id LIMIT {1} offset {2} """.format(select_union, limit, offset, filters)

        length = """ SELECT count(name_id) FROM (SELECT foo.name_id 
                                                    FROM ({0}) foo {1}) foo_join """.format(select_union, filters)

    else:
        case_when = ""
        for i in entities:
            case_when += """ min(CASE WHEN key = $${0}$$ then value end) as "{0}",""".format(i)
        case_when = case_when[:-1]

        sql = """ SELECT foo.name_id,case_id,measurement,{1}
                    FROM (SELECT name_id,case_id,measurement,key,STRING_AGG(value, ';') value 
                            FROM ({0}) foo2
                            group by name_id,case_id,measurement,key) foo
                    {4}
                    group by foo.name_id,case_id,measurement order by name_id 
                    LIMIT {2} offset {3} 
                    """.format(select_union, case_when, limit, offset, filters)

        length = """ SELECT count(name_id) FROM (SELECT foo.name_id
                    FROM ({0}) foo {1} group by foo.name_id,case_id,measurement) foo2 """.format(select_union, filters)

    try:
        df = pd.read_sql(sql, r.connection())
        length = pd.read_sql(length, r.connection())
        length = length.iloc[0]['count']
        return df, length, None
    except (Exception,):
        df = pd.DataFrame()
        length = 0
        return df, length, "Problem with load data from database"


def get_basic_stats(entity, measurement, date_filter, limit_filter, update_filter, r):

    filters, limit_selected, date_value1, date_value2, date_value = checking_for_filters(date_filter, limit_filter,
                                                                                         update_filter)
    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"

    n = """SELECT COUNT(DISTINCT name_id) FROM Patient"""
    if limit_selected:
        sql_part = ""
        for e in entity:
            s = """ (SELECT key,measurement,foo.name_id, AVG(value) as value
                    FROM examination_numerical foo 
                    {3}
                    WHERE key = $${0}$$ 
                    AND measurement IN ({1}) 
                    {2}
                    GROUP BY foo.name_id,key,measurement
                    {4})
                    UNION """.format(e, measurement, date_value, filters, limit_selected)
            sql_part = sql_part + s
        sql_part = sql_part[:-6]
    else:
        sql_part = """ SELECT foo.name_id,key,measurement,AVG(value) as value 
                        FROM examination_numerical foo
                        {3}
                        WHERE key IN ({0})
                        AND measurement IN ({1}) 
                        {2}
                        GROUP BY foo.name_id,key,measurement """.format(entity_final, measurement, date_value, filters)
    sql = """ WITH basic_stats as ({})
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
                                """.format(sql_part)

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

    filters, limit_selected, date_value1, date_value2, date_value = checking_for_filters(date_filter, limit_filter,
                                                                                         update_filter)
    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"

    n = """SELECT COUNT ( DISTINCT name_id) FROM Patient"""
    if limit_selected:
        sql_part = ""
        for e in entity:
            s = """ (SELECT key,measurement,foo.name_id
                    FROM {5} foo
                    {3}
                    WHERE key = $${0}$$ 
                    AND measurement IN ({1}) 
                    {2}
                    GROUP BY foo.name_id,key,measurement
                    {4} )
                    UNION """.format(e, measurement, date_value, filters, limit_selected, table)
            sql_part = sql_part + s
        sql_part = sql_part[:-6]
    else:
        sql_part = """SELECT foo.name_id,key,measurement
                                       FROM {4} foo
                                       {3}
                                       WHERE key IN ({0})
                                       AND measurement IN ({1}) 
                                       {2}
                                       GROUP BY foo.name_id,key,measurement""".format(entity_final, measurement,
                                                                                      date_value, filters, table)

    sql = """ WITH basic_stats AS ({})
                SELECT key,measurement,count(name_id) 
                    FROM basic_stats
                    GROUP BY measurement,key 
                    ORDER by key""".format(sql_part)

    try:
        n = pd.read_sql(n, r.connection())
        n = n['count']
        df = pd.read_sql(sql, r.connection())
        df['count NaN'] = int(n) - df['count']
        return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_scatter_plot(add_group_by, axis, measurement, categorical_entities, date_filter, limit_filter, update_filter,
                     r):

    filters, limit_selected, date_value1, date_value2, date_value = checking_for_filters(date_filter, limit_filter,
                                                                                         update_filter)
    subcategory = "$$" + "$$,$$".join(categorical_entities[1]) + "$$"

    if not add_group_by:
        sql = """SELECT foo.name_id,AVG(foo.value) as "{2}_{0}",AVG(y.value) as "{3}_{1}"
                            FROM examination_numerical foo
                            {6}
                            INNER JOIN examination_numerical as y
                                ON foo.name_id = y.name_id
                            WHERE foo.key IN ('{0}') 
                            AND y.key IN ('{1}') 
                            AND foo.measurement='{2}' 
                            AND y.measurement='{3}' 
                            {4}
                            {5}
                            GROUP BY foo.name_id
                            {7}""".format(axis[0], axis[1], measurement[0], measurement[1], date_value1, date_value2,
                                          filters, limit_selected)
    else:
        sql = """SELECT * FROM (
        SELECT foo.name_id,AVG(foo.value) as "{2}_{0}",AVG(y.value) as "{3}_{1}",
        STRING_AGG(distinct ec.value,'<br>') as "{6}" 
                            FROM examination_numerical foo
                            {8}
                            INNER JOIN examination_numerical y
                                ON foo.name_id = y.name_id
                            LEFT JOIN examination_categorical ec
                                ON foo.name_id = ec.name_id
                            WHERE foo.key IN ('{0}') 
                            AND y.key IN ('{1}') 
                            AND ec.key IN ('{6}')
                            AND foo.measurement='{2}' 
                            AND y.measurement='{3}' 
                            {4}
                            {5}
                            GROUP BY foo.name_id
                            {9}) foo2
                            WHERE foo2."{6}" IN ({7})
                            """.format(axis[0], axis[1], measurement[0], measurement[1], date_value1, date_value2,
                                       categorical_entities[0], subcategory, filters, limit_selected)

    try:
        df = pd.read_sql(sql, r.connection())
        x_axis, y_axis = axis[0] + '_' + measurement[0], axis[1] + '_' + measurement[1]
        if not add_group_by:
            df.columns = ['name_id', x_axis, y_axis]
        else:
            df.columns = ['name_id', x_axis, y_axis, categorical_entities[0]]
        if df.empty:
            df, error = df, "One of the selected entities is empty"
            return df, error
        else:
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_bar_chart(categorical_entities, measurement, date_filter, limit_filter, update_filter, r):

    filters, limit_selected, date_value1, date_value2, date_value = checking_for_filters(date_filter, limit_filter,
                                                                                         update_filter)
    subcategory = "$$" + "$$,$$".join(categorical_entities[1]) + "$$"
    measurement = "'" + "','".join(measurement) + "'"

    sql = """SELECT value AS "{0}",measurement,count(value)
                FROM (SELECT STRING_AGG(distinct value,'<br>')  AS value,measurement FROM examination_categorical foo
                        {4} 
                        WHERE key='{0}'
                        AND value IN ({1}) 
                        {3}
                        AND measurement IN ({2})
                        GROUP BY foo.name_id,measurement
                        {5}) AS foo2
                GROUP BY value,measurement
                """.format(categorical_entities[0], subcategory, measurement, date_value, filters, limit_selected)
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


def get_histogram_box_plot(entities, measurement, date_filter, limit_filter, update_filter, r):

    filters, limit_selected, date_value1, date_value2, date_value = checking_for_filters(date_filter, limit_filter,
                                                                                         update_filter)
    subcategory = "$$" + "$$,$$".join(entities[2]) + "$$"
    measurement = "'" + "','".join(measurement) + "'"

    sql = """SELECT foo.name_id,foo.measurement,AVG(foo.value) AS "{0}",ec.value AS "{1}"
                FROM examination_numerical foo 
                {5}
                LEFT JOIN examination_categorical ec
                ON foo.name_id = ec.name_id
                WHERE foo.key = '{0}' 
                AND ec.key = '{1}' 
                AND ec.value IN ({2}) 
                AND foo.measurement IN ({3}) 
                {4}
                GROUP BY foo.name_id,foo.measurement,ec.value
                {6}
                """.format(entities[0], entities[1], subcategory, measurement, date_value, filters, limit_selected)
    df = pd.read_sql(sql, r.connection())
    try:
        df = pd.read_sql(sql, r.connection())
        if df.empty or len(df) == 0:
            return df, "The entity {0} or {1} wasn't measured".format(entities[0], entities[1])
        else:
            df.columns = ["name", 'measurement', entities[0], entities[1]]
            df[entities[1]] = df[entities[1]].str.wrap(30).replace(to_replace=[r"\\n", "\n"], value=["<br>", "<br>"],
                                                                   regex=True)
            return df, None
    except (Exception,):
        return None, "Problem with load data from database"


def get_heat_map(entities, date_filter, limit_filter, update_filter, r):

    filters, limit_selected, date_value1, date_value2, date_value = checking_for_filters(date_filter, limit_filter,
                                                                                         update_filter)

    case_when = ""
    for i in entities:
        case_when += """ min(CASE WHEN key = $${0}$$ then value end) as "{0}",""".format(i)
    case_when = case_when[:-1]

    sql = """ SELECT foo.name_id,{0}
                FROM examination_numerical foo
                {1}
                group by foo.name_id
                {2} 
                """.format(case_when, filters, limit_selected)

    try:
        df = pd.read_sql(sql, r.connection())
        if df.empty:
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

# Not used now
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