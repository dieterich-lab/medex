import pandas as pd
import numpy as np
import datetime
import time
from collections import ChainMap
import textwrap as tr


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
    # case_id filter
    if len(case_id) != 0:
        case_id_filter = """ SELECT "Name_ID" FROM temp_table_case_ids """

    measurement_filter = "$$" + measurement + "$$"

    if categorical_filter and old_update[0] != update[0]:

        old_update[0] = update[0]

        cat = categorical_filter[int(update[0]) - 1]
        cat = cat.replace('<br>', ',')
        cat = "$$" + cat[(cat.find(' is') + 6):].replace(",", "$$,$$") + "$$"

        query = """ SELECT "Name_ID" from examination_categorical WHERE "Key" = '{}' and "Value" in ({}) 
                    and measurement = {} """.format(categorical[int(update[0]) - 1], cat, measurement_filter)
        query2 = """ SELECT "Name_ID","Key" from examination_categorical WHERE "Key" = '{}' and "Value" in ({}) 
                    and measurement = {} """.format(categorical[int(update[0]) - 1], cat, measurement_filter)

    if numerical_filter_name and old_update[1] != update[1]:

        old_update[1] = update[1]

        query = """ SELECT "Name_ID" from examination_numerical WHERE "Key" = '{}' and "Value" between {} and {} 
                    and measurement = {} """.format(numerical_filter_name[int(update[1]) - 1],
                                                    from1[int(update[1]) - 1],
                                                    to1[int(update[1]) - 1], measurement_filter)
        query2 = """ SELECT "Name_ID","Key" from examination_numerical WHERE "Key" = '{}' and "Value" between {} and {} 
                    and measurement = {} """.format(numerical_filter_name[int(update[1]) - 1],
                                                    from1[int(update[1]) - 1],
                                                    to1[int(update[1]) - 1], measurement_filter, )

    if update[0] == '0' and update[1] == '0':
        old_update[0], old_update[1] = update[0], update[1]

        sql_drop = "DROP TABLE IF EXISTS temp_table_name_ids"
        sql_drop_2 = "DROP TABLE IF EXISTS temp_table_ids"
        try:
            start_time = time.time()
            cur.execute(sql_drop)
            print("--- %s seconds ---" % (time.time() - start_time))
        except ValueError:
            print('something wrong')
        #finally:
        #    start_time = time.time()
        #    cur.execute(sql_drop_2)
        #    print("--- %s seconds ---" % (time.time() - start_time))
    elif (update[0] == '1' and update[1] == '0') or (update[0] == '0' and update[1] == '1'):
        sql_drop = "DROP TABLE IF EXISTS temp_table_name_ids"
        sql_drop_2 = "DROP TABLE IF EXISTS temp_table_ids"
        create_table = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_name_ids as ({}) """.format(query)
        create_table_2 = """ CREATE TEMP TABLE IF NOT EXISTS temp_table_ids as ({}) """.format(query2)


        try:
            start_time = time.time()
            cur.execute(sql_drop)
            cur.execute(create_table)
            print("--- %s seconds ---" % (time.time() - start_time))
        except ValueError:
            print('something wrong')
        #finally:
        #    start_time = time.time()
        #    cur.execute(sql_drop_2)
        #    cur.execute(create_table_2)
        #    print("--- %s seconds ---" % (time.time() - start_time))

    else:
        update_table = """ DELETE FROM temp_table_name_ids ttni WHERE "Name_ID" NOT IN ({})""".format(query)
        update_table_2 = """ INSERT INTO temp_table_ids ({}) """.format(query2)

        try:
            start_time = time.time()
            cur.execute(update_table)
            print("--- %s seconds ---" % (time.time() - start_time))
        except ValueError:
            print('something wrong')
        #finally:
        #    start_time = time.time()
        #    cur.execute(update_table_2)
        #    print("--- %s seconds ---" % (time.time() - start_time))

    """ SELECT "Name_ID" FROM where "Key" in () group by "Name_ID" having count("Name_ID") = {} """

    # categorical_filter
    category_filter = ""
    numerical_filter = ""
    category_filter_where = ""
    numerical_filter_where = ""

    for i in range(len(categorical)):
        cat = categorical_filter[i]
        cat = cat.replace('<br>',',')
        cat = "$$"+cat[(cat.find(' is') + 6):].replace(",", "$$,$$")+"$$"
        category_m = 'a_{}'.format(i)
        category_m0 = 'a_{}'.format(i-1)

        if i == 0:
            cat_filter = """Select {0}."Name_ID" FROM examination_categorical as {0}   """.format(category_m)

            cat_filter_where = """where {0}."Key"=$${1}$$ and {0}."Value" in ({2}) and 
                                    {0}.measurement in ({3}) """.format(category_m, categorical[i], cat,
                                                                        measurement_filter)
        else:
            cat_filter = """inner join examination_categorical as {0} 
                            on {1}."Name_ID"={0}."Name_ID" """.format(category_m, category_m0)

            cat_filter_where = """ and {3}."Key"=$${0}$$ and {3}."Value" in ({1}) 
                                    and {3}.measurement in ({2}) """.format(categorical[i], cat, measurement_filter,
                                                                            category_m)
        category_filter = category_filter + cat_filter
        category_filter_where = category_filter_where + cat_filter_where
    category_filter = category_filter + category_filter_where

    for i in range(len(from1)):
        numeric_m = 'b_{}'.format(i)
        numeric_m0 = 'b_{}'.format(i-1)
        if i == 0:
            num_filter = """Select {0}."Name_ID" FROM examination_numerical as {0}   """.format(numeric_m)

            num_filter_where = """where {0}."Key"=$${1}$$ and {0}."Value" between $${2}$$ and $${3}$$ and 
                                    {0}.measurement in ({4}) """.format(numeric_m, numerical_filter_name[i], from1[i],
                                                                        to1[i], measurement_filter,)

        else:
            num_filter = """inner join examination_numerical as {0} 
                            on {1}."Name_ID" = {0}."Name_ID" """.format(numeric_m, numeric_m0)

            num_filter_where = """ and {4}."Key"=$${0}$$ and {4}."Value" between $${1}$$ and $${2}$$ 
                                    and {4}.measurement in ({3}) """.format(numerical_filter_name[i], from1[i], to1[i],
                                                                            measurement_filter, numeric_m)
        numerical_filter = numerical_filter + num_filter
        numerical_filter_where = numerical_filter_where + num_filter_where
    numerical_filter = numerical_filter + numerical_filter_where

    # join filters
    if categorical_filter and case_id and numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" inner join ({2}) AS c
        on b."Name_ID" = c."Name_ID" """.format(category_filter, numerical_filter, case_id_filter)
    elif not case_id and categorical_filter and numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" """.format(
            category_filter, numerical_filter )
    elif case_id and not categorical_filter and numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" """.format(
            case_id_filter, numerical_filter)
    elif case_id and categorical_filter and not numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" """.format(
            case_id_filter, category_filter)
    elif not case_id and not categorical_filter and numerical_filter_name:
        sql = numerical_filter
    elif not case_id and not numerical_filter_name and categorical_filter:
        sql = category_filter
    elif case_id and not categorical_filter and not numerical_filter_name:
        sql = case_id_filter
    else:
        sql = ''

    print(sql)

    return None


def get_data(entity, what_table, measurement, date, update, r):
    """
    param:
     entity: entities names which should be selected from database
     what_table: How the data should be present as long table or entities as columns
     measurement: selected measurements
     r: connection with database
    return: DataFrame with all selected entities
    """
    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    entity_to_select =[x.replace("'","''") for x in entity]
    entity_final_l = "$$" + "$$,$$".join(entity_to_select) + "$$"
    entity_column = '"'+'" text,"'.join(entity) + '" text'
    measurement = "'" + "','".join(measurement) + "'"

    if update[0] == '0' and update[1] == '0':
        filter_en, filter_ec, filter_ed = '', '', ''
    else:
        filter_en = """ inner join temp_table_name_ids as ttni on en."Name_ID"=ttni."Name_ID" """
        filter_ec = """ inner join temp_table_name_ids as ttni on ec."Name_ID"=ttni."Name_ID" """
        filter_ed = """ inner join temp_table_name_ids as ttni on ed."Name_ID"=ttni."Name_ID" """

    sql = """SELECT en."Name_ID","measurement","Date","Key","Value"::text 
                    FROM examination_numerical as en
                    {4}
                    WHERE "Key" IN ({0})  
                    AND measurement IN ({1}) 
                    AND "Date" BETWEEN '{2}' AND '{3}'
                    UNION
                    SELECT ec."Name_ID","measurement","Date","Key","Value"
                    FROM examination_categorical as ec
                    {5}
                    WHERE "Key" IN ({0}) 
                    AND measurement IN ({1}) 
                    AND "Date" BETWEEN '{2}' and '{3}'
                    UNION
                    SELECT ed."Name_ID","measurement","Date","Key","Value"::text
                    FROM examination_date as ed
                    {6}
                    WHERE "Key" IN ({0}) 
                    AND measurement IN ({1}) 
                    AND "Date" BETWEEN '{2}' and '{3}'
                    """.format(entity_final, measurement, date[0], date[1], filter_en, filter_ec, filter_ed)

    sql2 = """SELECT * FROM crosstab('SELECT dense_rank() OVER (ORDER BY "measurement","Name_ID")::text AS row_name,* 
                                            FROM (SELECT en."Name_ID","measurement","Date","Key",
                                                            STRING_AGG("Value"::text,'';'') "Value"
                                                    FROM examination_numerical as en
                                                    {5}
                                                    WHERE  "Key" IN ({0})
                                                    GROUP BY en."Name_ID","measurement","Date","Key"
                                                    UNION
                                                    SELECT ed."Name_ID","measurement","Date","Key",
                                                            STRING_AGG("Value"::text,'';'') "Value"
                                                    FROM examination_date as ed
                                                    {7}
                                                    WHERE  "Key" IN ({0})
                                                    GROUP BY ed."Name_ID","measurement","Date","Key"
                                                    UNION
                                                    SELECT ec."Name_ID","measurement","Date","Key",
                                                            STRING_AGG("Value",'';'') "Value"
                                                    FROM examination_categorical as ec
                                                    {6}
                                                    WHERE "Key" IN ({0})
                                                    GROUP BY ec."Name_ID","measurement","Date","Key"
                                                    ) AS k  
                                                    ORDER BY row_name',
                                            'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) ORDER BY "order"') 
                                            AS ct (row_name text,"Name_ID" text,"measurement" text,"Date" text,{2}) 
                    WHERE "Date" BETWEEN '{3}' AND '{4}' 
                    AND "measurement" IN ({1}) 
                    ORDER BY "Name_ID", measurement 
                    """.format(entity_final_l, measurement, entity_column, date[0], date[1], filter_en, filter_ec,
                               filter_ed)

    try:
        if what_table == 'long':
            df = pd.read_sql(sql, r)
        else:
            df = pd.read_sql(sql2, r)
            df = df.drop(['row_name'], axis=1)
        return df, None
    except ValueError:
        df = pd.DataFrame()
        return df, "Problem with load data from database"


def get_basic_stats(entity, measurement, date, update, r):
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
    if update[0] == '0' and update[1] == '0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on en."Name_ID"=ttni."Name_ID" """

    sql = """SELECT "Key","measurement",
                    count(DISTINCT en."Name_ID"),
                    min("Value"),
                    max("Value"),
                    AVG("Value") AS "mean",
                    stddev("Value"),
                    (stddev("Value")/sqrt(count("Value"))) AS "stderr",
                    (percentile_disc(0.5) within group (order by "Value")) AS median 
                    FROM examination_numerical as en  
                    {4}
                    WHERE "Key" IN ({0}) 
                    AND "measurement" IN ({1}) 
                    AND "Date" BETWEEN '{2}' AND '{3}'
                    GROUP BY "Key","measurement" 
                    ORDER BY "Key","measurement" """.format(
                    entity_final, measurement, date[0], date[1], filter)

    try:
        df = pd.read_sql(sql, r)
        df['count NaN'] = int(n) - df['count']
        df = df.round(2)
        return df, None
    except ValueError:
        return None, "Problem with load data from database"


def get_cat_basic_stats(entity, measurement, date, update, r):
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
    if update[0] == '0' and update[1] == '0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on ec."Name_ID"=ttni."Name_ID" """

    sql = """SELECT "Key","measurement",count(DISTINCT ec."Name_ID") 
                FROM examination_categorical as ec
                {4}
                WHERE "Key" IN ({0}) 
                AND "measurement" IN ({1})
                AND "Date" BETWEEN '{2}' AND '{3}'
                GROUP BY "measurement","Key" """.format(entity_final, measurement, date[0], date[1], filter)

    try:
        df = pd.read_sql(sql, r)
        df['count NaN'] = int(n) - df['count']
        return df, None
    except ValueError:
        return None, "Problem with load data from database"


def get_date_basic_stats(entity, measurement, date, update, r):
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
    if update[0] == '0' and update[1] == '0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on ed."Name_ID"=ttni."Name_ID" """

    sql = """SELECT "Key","measurement",count(DISTINCT ed."Name_ID") 
                FROM examination_date as ed
                {4}            
                WHERE "Key" IN ({0}) 
                AND "measurement" IN ({1})
                AND "Date" BETWEEN '{2}' AND '{3}'
                GROUP BY "measurement","Key" """.format(entity_final, measurement, date[0], date[1], filter)

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


def get_scatter_plot(add_group_by, entity, subcategory, x_entity, y_entity, x_measurement,y_measurement, date, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """

    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    if update[0] == '0' and update[1] == '0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on x."Name_ID"=ttni."Name_ID" """

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
                            AND x."Date" BETWEEN '{4}' AND '{5}' 
                            AND y."Date" BETWEEN '{4}' AND '{5}'
                            GROUP BY x."Name_ID",y."Name_ID"  """.format(x_entity, y_entity, x_measurement,
                                                                         y_measurement, date[0], date[1], filter)
    else:
        sql = """SELECT x."Name_ID",AVG(x."Value") as "{2}_{0}",AVG(y."Value") as "{3}_{1}",STRING_AGG(distinct ec."Value",'<br>') as "{6}" 
                            FROM examination_numerical as x
                            {8}
                            INNER JOIN examination_numerical as y
                                ON x."Name_ID" = y."Name_ID"
                            LEFT JOIN examination_categorical as ec
                                ON x."Name_ID" = ec."Name_ID"
                            WHERE x."Key" IN ('{0}') 
                            AND y."Key" IN ('{1}') 
                            AND ec."Key" IN ('{6}')
                            AND ec."Value" IN ({7})
                            AND x."measurement"='{2}' 
                            AND y."measurement"='{3}' 
                            AND x."Date" BETWEEN '{4}' AND '{5}' 
                            AND y."Date" BETWEEN '{4}' AND '{5}'
                            GROUP BY x."Name_ID"  """.format(x_entity, y_entity, x_measurement,
                                                             y_measurement, date[0], date[1], entity, subcategory,filter)
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


def get_bar_chart(entity, subcategory, measurement, date, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """

    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update[0] == '0' and update[1] == '0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on ec."Name_ID"=ttni."Name_ID" """

    sql = """SELECT "Value" AS "{0}","measurement",count("Value")
                FROM (SELECT STRING_AGG(distinct "Value",'<br>')  AS "Value","measurement" FROM examination_categorical as ec
                        {5} 
                        WHERE "Key"='{0}'
                        AND "Value" IN ({1}) 
                        AND "Date" BETWEEN '{3}' AND '{4}'
                        AND "measurement" IN ({2})
                        GROUP BY ec."Name_ID",measurement) AS foo
                GROUP BY "Value","measurement" """.format(entity, subcategory, measurement, date[0], date[1],filter)

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


def get_histogram_box_plot(entity_num, entity_cat, subcategory, measurement, date, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """
    
    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if update[0] == '0' and update[1] == '0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on en."Name_ID"=ttni."Name_ID" """

    sql = """SELECT en."Name_ID",en."measurement",AVG(en."Value") AS "{0}",ec."Value" AS "{1}"
                FROM examination_numerical AS en
                {6} 
                LEFT JOIN examination_categorical AS ec 
                ON en."Name_ID" = ec."Name_ID"
                WHERE en."Key" = '{0}' 
                AND ec."Key" = '{1}' 
                AND ec."Value" IN ({2}) 
                AND en."measurement" IN ({3}) 
                AND en."Date" BETWEEN '{4}' AND '{5}'
                GROUP BY en."Name_ID",en."measurement",ec."Value"
                """.format(entity_num, entity_cat, subcategory, measurement, date[0], date[1],filter)
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


def get_heat_map(entity, date, update, r):
    """
    param:
     entity: categorical entities names which should be selected from database
     measurement: selected measurements
     r: connection with database
    return: DataFrame with calculated basic statistic
    """

    case_statement = ""
    crosstab_columns = ""
    if update[0] == '0' and update[1] == '0':
        filter =''
    else:
        filter = """ inner join temp_table_name_ids as ttni on en."Name_ID"=ttni."Name_ID" """
    for ent in entity:
        create_case_statement = """CASE WHEN "Key" = '{0}' THEN "Value" END AS "{0}" """.format(ent)
        case_statement = case_statement + ',' + create_case_statement
        create_crosstab_columns = '"{}" double precision'.format(ent)
        crosstab_columns = crosstab_columns + ',' + create_crosstab_columns

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    sql = """SELECT en."Name_ID","Key",AVG("Value") as "Value" 
                FROM examination_numerical as en
                {3} 
                WHERE "Key" IN ({0}) 
                AND "Date" BETWEEN '{1}' AND '{2}'
                GROUP BY en."Name_ID","Key" """.format(entity_fin, date[0], date[1],filter)
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