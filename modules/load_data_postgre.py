import pandas as pd
import numpy as np
import datetime
import time
from collections import ChainMap
import textwrap as tr
from threading import Thread


def get_header(r):
    """
    :param r: connection with database
    :return: data from header table
    """
    try:
        sql = "SELECT * FROM header"
        df = pd.read_sql(sql, r)
        name_id, measurement_name = df['Name_ID'][0], df['measurement'][0]
    except ValueError:
        name_id, measurement_name = 'Name_ID', 'measurement'
    return name_id, measurement_name


def get_date(r):
    """
    :param r: connection with database
    :return: get the first and last date on which the data were collected
    """
    try:
        sql = """ SELECT min("Date"),max("Date") FROM examination_numerical """
        df = pd.read_sql(sql, r)
        start_date = datetime.datetime.strptime(df['min'][0], '%Y-%m-%d').timestamp() * 1000
        end_date = datetime.datetime.strptime(df['max'][0], '%Y-%m-%d').timestamp() * 1000
    except ValueError:
        now = datetime.datetime.now()
        start_date = datetime.datetime.timestamp(now - datetime.timedelta(days=365.24*100)) * 1000
        end_date = datetime.datetime.timestamp(now) * 1000
    return start_date, end_date


def patient(r):
    """
    :param r: connection with database
    :return: Patient ID list
    """
    try:
        sql = """SELECT * FROM Patient"""
        df = pd.read_sql(sql, r)
        return df['Name_ID'], None
    except ValueError:
        return None, "Problem with load data from database"


def get_entities(r):
    """
    :param r: connection with database
    :return: DataFrame with entities names and their description
    """
    all_entities = """SELECT "Key","description","synonym" FROM name_type ORDER BY "order" """

    try:
        all_entities = pd.read_sql(all_entities, r)
        all_entities = all_entities.replace([None], ' ')
    except ValueError:
        all_entities = pd.DataFrame(columns=["Key", "description", "synonym"])
    return all_entities


def get_numeric_entities(r):
    """
    param r: connection with database
    return:
        size: number of numerical entities
        entities: DataFrame with name, synonym,description for numerical entities
        df_min_max: DataFrame with min and max values
    """
    size = """SELECT count(*) FROM examination_numerical"""
    all_numerical_entities = """SELECT "Key","description","synonym" FROM name_type WHERE type = 'Double'
                                ORDER BY "Key" """
    min_max = """SELECT "Key",max("Value"),min("Value") FROM examination_numerical GROUP BY "Key" """

    try:
        df = pd.read_sql(size, r)
        size = df.iloc[0]['count']

        entities = pd.read_sql(all_numerical_entities, r)
        entities = entities.replace([None], ' ')

        df_min_max = pd.read_sql(min_max, r)
        df_min_max = df_min_max.set_index('Key')

    except ValueError:
        size = 0
        entities = pd.DataFrame(columns=["Key", "description", "synonym"])
        df_min_max = pd.DataFrame()
    return size, entities, df_min_max


def get_timestamp_entities(r):
    """
    param r: connection with database
    return:
        size: number of date entities
        entities: DataFrame with name, synonym,description for date entities
    """
    size = """SELECT count(*) FROM examination_date"""
    all_timestamp_entities = """ SELECT "Key","description","synonym" FROM name_type WHERE type IN ('Date','Time') 
                                 ORDER BY "Key" """

    try:
        df = pd.read_sql(size, r)
        size = df.iloc[0]['count']

        entities = pd.read_sql(all_timestamp_entities, r)
        entities = entities.replace([None], ' ')

    except ValueError:
        size = 0
        entities = pd.DataFrame(columns=["Key", "description", "synonym"])
    return size, entities


def get_categorical_entities(r):
    """
    param r: connection with database
    return:
        size: number of categorical entities
        entities: DataFrame with name, synonym,description for categorical entities
        df_subcategories: dictionary with subcategories for categorical entities
    """

    # Retrieve all categorical values
    examination_categorical_table_size = """SELECT count(*) FROM examination_categorical"""
    all_categorical_entities = """SELECT "Key","description","synonym" FROM name_type WHERE "type" = 'String' 
                                  ORDER BY "Key" """

    # Retrieve categorical values with subcategories
    all_subcategories = """SELECT DISTINCT "Key","Value" FROM examination_categorical ORDER by "Key" """

    try:
        size = pd.read_sql(examination_categorical_table_size, r)
        size = size.iloc[0]['count']
        entities = pd.read_sql(all_categorical_entities, r)
        subcategories = pd.read_sql(all_subcategories, r)

        array = []
        df_subcategories = {}
        # create dictionary with categories and subcategories
        for value in entities['Key']:
            df = subcategories[subcategories["Key"] == value]
            del df['Key']
            df_subcategories[value] = list(df['Value'])
            array.append(df_subcategories)

        df_subcategories = dict(ChainMap(*array))

        return size, entities, df_subcategories
    except ValueError:
        array = []
        size = 0
        entities = pd.DataFrame(columns=["Key", "description", "synonym"])
        df_subcategories = dict(ChainMap(*array))
        return size, entities, df_subcategories


def get_measurement(r):
    """
    param r: connection with database
    return: return column with measurements
    """
    try:
        # add the information about measurement to other table MAYBE
        sql = """SELECT DISTINCT "measurement":: int FROM examination_numerical ORDER BY "measurement" """
        df = pd.read_sql(sql, r)
        df['measurement'] = df['measurement'].astype(str)
        return df['measurement']
    except ValueError:
        return ["No data"]


def create_temp_table(case_id,rdb):
    case_id_all = "$$" + "$$,$$".join(case_id) + "$$"
    sql_drop = "DROP TABLE IF EXISTS temp_table_case_ids"
    create_table = """ CREATE TEMP TABLE temp_table_case_ids as (SELECT "Name_ID" FROM patient where 
    "Case_ID" in ({0})) """.format(case_id_all)

    try:
        cur = rdb.cursor()
        cur.execute(sql_drop)
        cur.execute(create_table)
    except ValueError:
        print('something wrong')


old_update = ['0', '0']


def filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement, update, r):

    cur = r.cursor()
    cur2 = r.cursor()

    measurement_filter = "$$" + measurement + "$$"

    if categorical_filter and old_update[0] != update[0]:
        cat = categorical_filter[int(update[0]) - 1]
        cat = cat.replace('<br>', ',')
        cat = "$$" + cat[(cat.find(' is') + 6):].replace(",", "$$,$$") + "$$"

        query = """ SELECT "Name_ID" FROM examination_categorical WHERE "Key" = '{}' AND "Value" IN ({}) 
                    AND measurement = {} """.format(categorical[int(update[0]) - 1], cat, measurement_filter)
        query2 = """ SELECT "Name_ID","Key" FROM examination_categorical WHERE "Key" = '{}' AND "Value" IN ({}) 
                    AND measurement = {} """.format(categorical[int(update[0]) - 1], cat, measurement_filter)

    if numerical_filter_name and old_update[1] != update[1]:
        query = """ SELECT "Name_ID" FROM examination_numerical WHERE "Key" = '{}' AND "Value" BETWEEN {} AND {} 
                    AND measurement = {} """.format(numerical_filter_name[int(update[1]) - 1],from1[int(update[1]) - 1],
                                                    to1[int(update[1]) - 1], measurement_filter)
        query2 = """ SELECT "Name_ID","Key" FROM examination_numerical WHERE "Key" = '{}' AND "Value" BETWEEN {} AND {} 
                    AND measurement = {} """.format(numerical_filter_name[int(update[1]) - 1],from1[int(update[1]) - 1],
                                                    to1[int(update[1]) - 1], measurement_filter, )

    if int(old_update[0]) == int(update[0]) and int(old_update[1]) == int(update[1]):
        error = 'None'
    elif update[0] == '0' and update[1] == '0':
        """ If clean """
        old_update[0], old_update[1] = update[0], update[1]
        sql_drop = "DROP TABLE IF EXISTS temp_table_name_ids"
        sql_drop_2 = "DROP TABLE IF EXISTS temp_table_ids"
        try:
            Thread(target=cur.execute(sql_drop)).start()
            Thread(target=cur2.execute(sql_drop_2)).start()
        except ValueError:
            print('something wrong')
    elif int(old_update[0]) > int(update[0]) or int(old_update[1]) > int(update[1]):
        """ If filter removed """
        old_update[0], old_update[1] = update[0], update[1]
        if update[0] != '0' and update[1] != '0':
            filter_join = '$$' + '$$,$$'.join(categorical) + '$$,$$' + '$$,$$'.join(numerical_filter_name) + '$$'
        elif update[0] != '0' and update[1] == '0':
            filter_join = '$$' + '$$,$$'.join(categorical) + '$$'
        else:
            filter_join = '$$' + '$$,$$'.join(numerical_filter_name) + '$$'
        n = int(update[0]) + int(update[1])
        query = """ SELECT "Name_ID" FROM temp_table_ids WHERE "Key" IN ({}) GROUP BY "Name_ID" 
                    HAVING count("Name_ID") = {} """.format(filter_join, n)
        sql_drop_2 = "DROP TABLE IF EXISTS temp_table_name_ids"
        create_table = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_name_ids as ({}) """.format(query)
        update_table = """ DELETE FROM temp_table_ids WHERE "Key" not in ({}) """.format(filter_join)
        try:
            Thread(target=cur.execute(sql_drop_2)).start()
            Thread(target=cur.execute(create_table)).start()
            Thread(target=cur2.execute(update_table)).start()
            cur.execute(sql_drop_2)
            cur.execute(create_table)
        except ValueError:
            print('something wrong')
    elif (update[0] == '1' and update[1] == '0') or (update[0] == '0' and update[1] == '1'):
        """If first filter selected"""
        old_update[0], old_update[1] = update[0], update[1]
        create_table = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_name_ids as ({}) """.format(query)
        create_table_2 = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_ids as ({}) """.format(query2)
        try:
            Thread(target=cur.execute(create_table)).start()
            Thread(target=cur2.execute(create_table_2)).start()
        except ValueError:
            print('something wrong')
    elif int(old_update[0]) < int(update[0]) or int(old_update[1]) < int(update[1]):
        """ If next filters added """
        old_update[0], old_update[1] = update[0], update[1]
        update_table = """ NSERT INTO temp_table_name_ids WHERE "Name_ID" NOT IN ({})""".format(query)
        update_table_2 = """ INSERT INTO temp_table_ids ({}) """.format(query2)
        try:
            Thread(target=cur.execute(update_table)).start()
            Thread(target=cur2.execute(update_table_2)).start()
        except ValueError:
            print('something wrong')
    return None


def get_data(entity, categorical_entities, numerical_entities, date_entities, what_table, measurement, date,
             limit_selected, limit, offset, update, r):
    """
    param:
     entity: entities names which should be selected from database
     what_table: How the data should be present as long table or entities as columns
     measurement: selected measurements
     r: connection with database
    return: DataFrame with all selected entities
    """

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    entity_column_n, entity_column_c, entity_column_d = '', '', ''
    measurement = "$$" + "$$,$$".join(measurement) + "$$"
    sql_n, sql_c, sql_d = "", "", ""
    join_n, join_c, join_d = "", "", ""
    cte_table_n, cte_table_c, cte_table_d = "", "", ""

    if update == '0,0':
        filter_en, filter_ec, filter_ed = "", "", ""
    else:
        filter_en = """ inner join temp_table_name_ids as ttni on en."Name_ID"=ttni."Name_ID" """
        filter_ec = """ inner join temp_table_name_ids as ttni on ec."Name_ID"=ttni."Name_ID" """
        filter_ed = """ inner join temp_table_name_ids as ttni on ed."Name_ID"=ttni."Name_ID" """

    if limit_selected:
        limit = """ LIMIT {0} OFFSET {1}""".format(limit, offset)
    else:
        limit = ''

    if date[2] !=0:
        date_value = 'AND "Date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    if not limit_selected and what_table == 'long':
        sql = """(SELECT en."Name_ID","measurement","Date","Key","Value"::text
                         FROM examination_numerical as en
                         {3}
                         WHERE "Key" IN ({0})  
                         AND measurement IN ({1}) 
                         {2})
                         UNION
                         (SELECT ec."Name_ID","measurement","Date","Key","Value"::text
                         FROM examination_categorical as ec
                         {4}
                         WHERE "Key" IN ({0}) 
                         AND measurement IN ({1}) 
                         {2})
                         UNION
                         (SELECT ed."Name_ID","measurement","Date","Key","Value"::text
                         FROM examination_date as ed
                         {5}
                         WHERE "Key" IN ({0}) 
                         AND measurement IN ({1}) 
                         {2})
                         """.format(entity_final, measurement, date_value, filter_en, filter_ec, filter_ed)
    else:
        if numerical_entities:
            entity_column_n = '"' + '","'.join(numerical_entities) + '",'
            for i, e in enumerate(numerical_entities):
                if limit_selected:
                    sql_part_n = """(SELECT en."Name_ID","measurement","Date","Key","Value"::text
                                   FROM examination_numerical as en
                                   {4}
                                   WHERE "Key" = $${0}$$  
                                   AND measurement IN ({1}) 
                                   {2}
                                   {3}) UNION """.format(e, measurement, date_value, limit,filter_en)
                    sql_n = sql_n + sql_part_n
                if what_table != 'long':
                    tab = 'a_{}'.format(i)
                    cte_table = """,
                                    {0} as (SELECT en."Name_ID","Date",measurement,STRING_AGG("Value"::text, ';') "{1}"
                                    FROM examination_numerical en
                                    {5}
                                    WHERE "Key" = $${1}$$
                                    AND measurement IN ({2})
                                    {3}
                                    GROUP BY en."Name_ID","Date","Key","measurement"
                                    {4})""".format(tab, e, measurement, date_value, limit, filter_en)
                    cte_table_n = cte_table_n + cte_table
                    join = """ 
                            FULL OUTER JOIN {0} 
                            USING("Name_ID",measurement,"Date") """.format(tab)
                    join_n = join_n + join
        if categorical_entities:
            entity_column_c = '"' + '","'.join(categorical_entities) + '",'
            for i, e in enumerate(categorical_entities):
                if limit_selected:
                    sql_part_c = """(SELECT ec."Name_ID","measurement","Date","Key","Value"::text
                                    FROM examination_categorical as ec
                                    {4}
                                    WHERE "Key" = $${0}$$  
                                    AND measurement IN ({1}) 
                                    {2}
                                    {3}) UNION """.format(e, measurement, date_value, limit, filter_ec)
                    sql_c = sql_c + sql_part_c
                if what_table != 'long':
                    tab = 'a_{}'.format(len(numerical_entities) + i)
                    cte_table = """,
                                    {0} as (SELECT ec."Name_ID","Date",measurement,STRING_AGG("Value"::text, ';') "{1}"
                                    FROM examination_categorical ec
                                    {5}
                                    WHERE "Key" = $${1}$$
                                    AND measurement IN ({2})
                                    {3}
                                    GROUP BY ec."Name_ID","Date","Key","measurement"
                                    {4})""".format(tab, e, measurement, date_value, limit, filter_ec)
                    cte_table_c = cte_table_c + cte_table
                    join = """ 
                                FULL OUTER JOIN {0} 
                                USING("Name_ID",measurement,"Date") """.format(tab)
                    join_c = join_c + join
        if date_entities:
            entity_column_d = '"' + '","'.join(date_entities) + '",'
            for i,e in enumerate(date_entities):
                if limit_selected:
                    sql_part_d = """(SELECT ed."Name_ID","date","measurement","Date","Key","Value"::text
                                    FROM examination_date as ed 
                                    {4}
                                    WHERE "Key" = $${0}$$  
                                    AND measurement IN ({1}) 
                                    {2}
                                    {3}) UNION """.format(e, measurement,  date_value, limit, filter_ed)
                    sql_d = sql_d + sql_part_d
                if what_table != 'long':
                    tab = 'a_{}'.format(len(numerical_entities) + len(categorical_entities) + i)
                    cte_table = """,
                                    {0} as (SELECT ed."Name_ID",measurement,"Date",STRING_AGG("Value"::text, ';') "{1}"
                                    FROM examination_date ed
                                    {5}
                                    WHERE "Key" = $${1}$$
                                    AND measurement IN ({2})
                                    {3}
                                    GROUP BY "Name_ID","Date","Key","measurement"
                                    {4} )""".format(tab, e, measurement, date_value, limit, filter_ed)
                    cte_table_d = cte_table_d + cte_table
                    join = """
                            FULL OUTER JOIN {0} 
                            USING("Name_ID","Date",measurement) """.format(tab, 'a_{}'.format(len(numerical_entities) + len(categorical_entities) + i-1))
                    join_c = join_c + join
        if what_table != 'long':
            sql2_part1 = "WITH" + cte_table_n + cte_table_c + cte_table_d + """ SELECT "Name_ID","Date",measurement, """ + \
                       entity_column_n + entity_column_c + entity_column_d
            sql2_part2 = " From a_0" + join_n + join_c + join_d
            sql2 = sql2_part1[:-1]+sql2_part2
            start = sql2.find(',')
            start_full = sql2.find('FULL')
            sql2 = sql2[0:start] + sql2[start+1:start_full] + sql2[start_full+100::]
        else:
            sql = sql_n + sql_c + sql_d
            sql = sql[:-6]

    try:
        if what_table == 'long':
            df = pd.read_sql(sql, r)
        else:
            df = pd.read_sql(sql2, r)
        return df, None
    except ValueError:
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

    n = """SELECT COUNT ( DISTINCT "Name_ID") FROM Patient"""
    n = pd.read_sql(n, r)
    n = n['count']

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update == '0,0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on en."Name_ID"=ttni."Name_ID" """
    if date[2] !=0:
        date_value = 'AND "Date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql = """ WITH basic_stats as (SELECT en."Name_ID","Key","measurement",AVG("Value") as "Value" 
                                   FROM examination_numerical en 
                                   {3}
                                   WHERE "Key" IN ({0})
                                   AND "measurement" IN ({1}) 
                                   {2}
                                   GROUP BY "Name_ID","Key","measurement")
                SELECT "Key","measurement",
                                count("Name_ID"),
                                min("Value"),
                                max("Value"),
                                AVG("Value") AS "mean",
                                stddev("Value"),
                                (stddev("Value")/sqrt(count("Value"))) AS "stderr",
                                (percentile_disc(0.5) within group (order by "Value")) AS median 
                                FROM basic_stats
                                GROUP BY "Key","measurement" 
                                ORDER BY "Key","measurement"
                                """.format(
                                entity_final, measurement, date_value, filter)
    if limit_selected:
        sql_part = ""
        for e in entity:
            s = """ (SELECT "Key","measurement",en."Name_ID", AVG("Value") as "Value"
                    FROM examination_numerical as en  
                    {3}
                    WHERE "Key" = $${0}$$ 
                    AND "measurement" IN ({1}) 
                    {2}
                    GROUP BY en."Name_ID","Key","measurement"
                    LIMIT {4} OFFSET {5})
                    UNION """.format(e, measurement, date_value, filter, limit, offset)
            sql_part = sql_part + s
        sql_part = sql_part[:-6]
        sql = """ WITH basic_stats AS ({})
                    SELECT "Key","measurement",
                                    count("Name_ID"),
                                    min("Value"),
                                    max("Value"),
                                    AVG("Value") AS "mean",
                                    stddev("Value"),
                                    (stddev("Value")/sqrt(count("Value"))) AS "stderr",
                                    (percentile_disc(0.5) within group (order by "Value")) AS median 
                                    FROM basic_stats as en  
                                    GROUP BY "Key","measurement" 
                                    ORDER BY "Key","measurement" """.format(sql_part)
    try:
        df = pd.read_sql(sql, r)
        df['count NaN'] = int(n) - df['count']
        df = df.round(2)
        return df, None
    except ValueError:
        return None, "Problem with load data from database"


def get_cat_basic_stats(entity, measurement, date, limit_selected, limit, offset, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """

    n = """SELECT COUNT ( DISTINCT "Name_ID") FROM Patient"""
    n = pd.read_sql(n, r)
    n = n['count']

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update == '0,0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on ec."Name_ID"= ttni."Name_ID" """
    if date[2] !=0:
        date_value = 'AND "Date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql = """WITH basic_stats as (SELECT ec."Name_ID","Key","measurement"
                                   FROM examination_categorical as ec
                                   {3}
                                   WHERE "Key" IN ({0})
                                   AND "measurement" IN ({1}) 
                                   {2}
                                   GROUP BY "Name_ID","Key","measurement")
            SELECT "Key","measurement",count("Name_ID") 
                        FROM basic_stats
                        GROUP BY "measurement","Key" """.format(entity_final, measurement, date_value, filter)
    if limit_selected:
        sql_part = ""
        for e in entity:
            s = """ (SELECT "Key","measurement",ec."Name_ID"
                    FROM examination_categorical as ec 
                    {3}
                    WHERE "Key" = $${0}$$ 
                    AND "measurement" IN ({1}) 
                    {2}
                    GROUP BY ec."Name_ID","Key","measurement"
                    LIMIT {4} OFFSET {5})
                    UNION """.format(e, measurement, date_value, filter, limit, offset)
            sql_part = sql_part + s
        sql_part = sql_part[:-6]
        sql = """ WITH basic_stats AS ({})
                    SELECT "Key","measurement",count("Name_ID") 
                        FROM basic_stats
                        GROUP BY "measurement","Key" """.format(sql_part)
    try:
        df = pd.read_sql(sql, r)
        df['count NaN'] = int(n) - df['count']
        return df, None
    except ValueError:
        return None, "Problem with load data from database"


def get_date_basic_stats(entity, measurement, date, limit_selected, limit, offset, update, r):
    """
    param:
     entity: date entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """

    n = """SELECT COUNT ( DISTINCT "Name_ID") FROM Patient"""
    n = pd.read_sql(n, r)
    n = n['count']

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update == '0,0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on ed."Name_ID"=ttni."Name_ID" """
    if date[2] !=0:
        date_value = 'AND "Date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql = """WITH basic_stats as (SELECT ec."Name_ID","Key","measurement"
                                   FROM examination_date as ed
                                   {3}
                                   WHERE "Key" IN ({0})
                                   AND "measurement" IN ({1}) 
                                   {2}
                                   GROUP BY "Name_ID","Key","measurement")
            SELECT "Key","measurement",count("Name_ID") 
                        FROM basic_stats
                        GROUP BY "measurement","Key" """.format(entity_final, measurement, date_value, filter)
    if limit_selected:
        sql_part = ""
        for e in entity:
            s = """ (SELECT "Key","measurement",ed."Name_ID"
                    FROM examination_date as ed 
                    {3}
                    WHERE "Key" = $${0}$$ 
                    AND "measurement" IN ({1}) 
                    {2}
                    GROUP BY ed."Name_ID","Key","measurement"
                    LIMIT {4} OFFSET {5})
                    UNION """.format(e, measurement, date_value, filter, limit, offset)
            sql_part = sql_part + s
        sql_part = sql_part[:-6]
        sql = """ WITH basic_stats AS ({})
                    SELECT "Key","measurement",count("Name_ID") 
                        FROM basic_stats
                        GROUP BY "measurement","Key" """.format(sql_part)
    try:
        df = pd.read_sql(sql, r)
        df['count NaN'] = int(n) - df['count']
        return df, None
    except ValueError:
        return None, "Problem with load data from database"


# I have to work on this
def get_unit(name, r):
    """ Get number of all patients

     number use only for basic_stats
     """
    try:
        sql = """SELECT "Key","unit" FROM name_type WHERE "Key"='{}' """.format(name)
        df = pd.read_sql(sql, r)
        return df['unit'][0], None
    except ValueError:
        return None, "Problem with load data from database"


def get_scatter_plot(add_group_by, entity, subcategory, x_entity, y_entity, x_measurement,y_measurement, date, limit_selected, limit, offset, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """
    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    if update == '0,0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on x."Name_ID"=ttni."Name_ID" """
    if limit_selected:
        limit_selected = """ LIMIT {} OFFSET {} """.format(limit, offset)
    else:
        limit_selected = ''
    if date[2] !=0:
        date_value1 = 'AND x."Date" BETWEEN $${0}$$ AND $${1}$$ '.format(date[0], date[1])
        date_value2 = 'AND y."Date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value1 = ''
        date_value2 = ''
    if add_group_by == False:
        sql = """SELECT x."Name_ID",AVG(x."Value") as "{2}_{0}",AVG(y."Value") as "{3}_{1}"
                            FROM examination_numerical as x
                            {6}
                            INNER JOIN examination_numerical as y
                                ON x."Name_ID" = y."Name_ID"
                            WHERE x."Key" IN ('{0}') 
                            AND y."Key" IN ('{1}') 
                            AND x."measurement"='{2}' 
                            AND y."measurement"='{3}' 
                            {4}
                            {5}
                            GROUP BY x."Name_ID",y."Name_ID"
                            {7}""".format(x_entity, y_entity, x_measurement,
                                                                         y_measurement, date_value1,date_value2, filter, limit_selected)
    else:
        sql = """SELECT * FROM (SELECT x."Name_ID",AVG(x."Value") as "{2}_{0}",AVG(y."Value") as "{3}_{1}",STRING_AGG(distinct ec."Value",'<br>') as "{6}" 
                            FROM examination_numerical as x
                            {8}
                            INNER JOIN examination_numerical as y
                                ON x."Name_ID" = y."Name_ID"
                            LEFT JOIN examination_categorical as ec
                                ON x."Name_ID" = ec."Name_ID"
                            WHERE x."Key" IN ('{0}') 
                            AND y."Key" IN ('{1}') 
                            AND ec."Key" IN ('{6}')
                            AND x."measurement"='{2}' 
                            AND y."measurement"='{3}' 
                            {4}
                            {5}
                            GROUP BY x."Name_ID"
                            {9}) foo
                            WHERE foo."{6}" IN ({7})
                            """.format(x_entity, y_entity, x_measurement,
                                                             y_measurement, date_value1,date_value2, entity, subcategory,filter,limit_selected)


    try:
        df = pd.read_sql(sql, r)
        x_axis_m = x_entity + '_' + x_measurement
        y_axis_m = y_entity + '_' + y_measurement
        if add_group_by == False:
            df.columns = ['Name_ID', x_axis_m, y_axis_m]
        else:
            df.columns = ['Name_ID', x_axis_m, y_axis_m,entity]
        if df.empty:
            df, error = df, "One of the selected entities is empty"
            return df, error
        else:
            return df, None
    except ValueError:
        return None, "Problem with load data from database"


def get_bar_chart(entity, subcategory, measurement, date, limit_selected, limit, offset, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """

    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update == '0,0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on ec."Name_ID"=ttni."Name_ID" """
    if limit_selected:
        limit_selected = """ LIMIT {} OFFSET {} """.format(limit, offset)
    else:
        limit_selected = ''
    if date[2] !=0:
        date_value = 'AND "Date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql = """SELECT "Value" AS "{0}","measurement",count("Value")
                FROM (SELECT STRING_AGG(distinct "Value",'<br>')  AS "Value","measurement" FROM examination_categorical as ec
                        {4} 
                        WHERE "Key"='{0}'
                        AND "Value" IN ({1}) 
                        {3}
                        AND "measurement" IN ({2})
                        GROUP BY ec."Name_ID",measurement
                        {5}) AS foo
                GROUP BY "Value","measurement"
                """.format(entity, subcategory, measurement, date_value, filter, limit_selected)
    try:
        df = pd.read_sql(sql, r)
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            df.columns = [entity, 'measurement', 'count']
            df[entity] = df[entity].str.wrap(30).replace(to_replace=[r"\\n", "\n"],
                                                         value=["<br>", "<br>"], regex=True)
            return df, None
    except ValueError:
        return None, "Problem with load data from database"


def get_histogram_box_plot(entity_num, entity_cat, subcategory, measurement, date, limit_selected, limit, offset, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """
    
    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update == '0,0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on en."Name_ID"=ttni."Name_ID" """
    if limit_selected:
        limit_selected = """ LIMIT {} OFFSET {} """.format(limit, offset)
    else:
        limit_selected = ''
    if date[2] !=0:
        date_value = 'AND en."Date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    sql = """SELECT en."Name_ID",en."measurement",AVG(en."Value") AS "{0}",ec."Value" AS "{1}"
                FROM examination_numerical AS en 
                {5}
                LEFT JOIN examination_categorical AS ec 
                ON en."Name_ID" = ec."Name_ID"
                WHERE en."Key" = '{0}' 
                AND ec."Key" = '{1}' 
                AND ec."Value" IN ({2}) 
                AND en."measurement" IN ({3}) 
                {4}
                GROUP BY en."Name_ID",en."measurement",ec."Value"
                {6}
                """.format(entity_num, entity_cat, subcategory, measurement, date_value, filter, limit_selected)
    try:
        df = pd.read_sql(sql, r)
        if df.empty or len(df) == 0:
            return df, "The entity {0} or {1} wasn't measured".format(entity_num, entity_cat)
        else:
            df.columns = ["Name", 'measurement', entity_num, entity_cat]
            df[entity_cat] = df[entity_cat].str.wrap(30).replace(to_replace=[r"\\n", "\n"],
                                                         value=["<br>", "<br>"], regex=True)
            return df, None
    except ValueError:
        return None, "Problem with load data from database"


def get_heat_map(entity, date, limit_selected, limit, offset, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """

    case_statement = ""
    crosstab_columns = ""
    if update == '0,0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on en."Name_ID"=ttni."Name_ID" """
    for ent in entity:
        create_case_statement = """CASE WHEN "Key" = '{0}' THEN "Value" END AS "{0}" """.format(ent)
        case_statement = case_statement + ',' + create_case_statement
        create_crosstab_columns = '"{}" double precision'.format(ent)
        crosstab_columns = crosstab_columns + ',' + create_crosstab_columns
    if date[2] !=0:
        date_value = 'AND en."Date" BETWEEN $${0}$$ AND $${1}$$'.format(date[0], date[1])
    else:
        date_value = ''
    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    sql = """SELECT en."Name_ID","Key",AVG("Value") as "Value" 
                FROM examination_numerical as en
                {2} 
                WHERE "Key" IN ({0}) 
                {1}
                GROUP BY en."Name_ID","Key" """.format(entity_fin, date_value, filter)

    if limit_selected:
        sql = ""
        for e in entity:
            sql_part = """(SELECT en."Name_ID","Key","Value" 
                           FROM examination_numerical as en 
                           {2}
                           WHERE "Key" = $${0}$$  
                           {1}
                           LIMIT {3} 
                           OFFSET {4}) UNION """.format(e, date_value, filter, limit, offset)
            sql = sql + sql_part
        sql = """ SELECT "Name_ID","Key",AVG("Value") as "Value" FROM (""" + sql[:-6] + """) foo GROUP BY "Name_ID","Key" """

    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Name_ID"], columns="Key", values="Value", aggfunc=np.mean).reset_index()
        new_columns = [tr.fill(x, width=20).replace("\n", "<br>") for x in df.columns.values]
        df.columns = new_columns
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except ValueError:
        return None, "Problem with load data from database"


def calculator(entity1, entity2, column_name, r):

    sql = """ SELECT a."Name_ID",a."measurement",
                DATE_PART('year',a."Value"::timestamp) - DATE_PART('year',b."Value"::timestamp) as "{2}" 
                FROM examination_date as a FULL JOIN examination_date as b on a."Name_ID" = b."Name_ID" 
                and a."measurement" = b."measurement" where a."Key"='{0}' and b."Key"='{1}' """.format(entity1, entity2, column_name)

    try:
        df = pd.read_sql(sql, r)
        return df
    except ValueError:
        return None