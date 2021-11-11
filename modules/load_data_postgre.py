import pandas as pd
import numpy as np
from datetime import datetime
from collections import ChainMap



def get_header(r):
    """
    :param r: connection with database
    :return: data from header table
    """
    try:
        sql = "Select * from header"
        df = pd.read_sql(sql, r)
        name_id, measurement_name = df['Name_ID'][0], df['measurement'][0]
    except Exception:
        name_id, measurement_name = 'Name_ID', 'measurement'
    return name_id, measurement_name


def get_date(r):
    """
    :param r: connection with database
    :return: get the first and last date on which the data were collected
    """
    try:
        sql = """ Select min("Date"),max("Date") from examination_numerical """
        df = pd.read_sql(sql, r)
        start_date = datetime.strptime(df['min'][0], '%Y-%m-%d').timestamp() * 1000
        end_date = datetime.strptime(df['max'][0], '%Y-%m-%d').timestamp() * 1000
    except Exception:
        now = datetime.now()
        start_date = datetime.timestamp(now) * 1000
        end_date = datetime.timestamp(now) * 1000
    return start_date, end_date


def get_entities(r):
    """
    :param r: connection with database
    :return: DataFrame with entities names and their description
            DataFrame with entities which should be showed on first page
    """
    all_entities = """SELECT "Key","description","synonym" FROM name_type order by "order" """
    show_on_first_page = """Select "Key" from name_type where "show" = '+' """

    try:
        all_entities = pd.read_sql(all_entities, r)
        all_entities = all_entities.replace([None], ' ')
        show_on_first_page = pd.read_sql(show_on_first_page, r)
    except Exception:
        all_entities = pd.DataFrame(columns=["Key", "description", "synonym"])
        show_on_first_page = pd.DataFrame(columns=['Key'])
    return all_entities, show_on_first_page


def get_numeric_entities(r):
    """

    :param r:
    :return:
    """
    size = """SELECT count(*) FROM examination_numerical"""
    all_numerical_entities = """Select "Key","description","synonym" from name_type where type = 'Double' order by "Key" """
    min_max = """Select distinct "Key",max("Value"[1]),min("Value"[1]) from examination_numerical group by "Key" """

    try:
        df = pd.read_sql(size, r)
        df = df.iloc[0]['count']

        df1 = pd.read_sql(all_numerical_entities, r)
        df1 = df1.replace([None], ' ')

        df_min_max = pd.read_sql(min_max, r)
        df_min_max = df_min_max.set_index('Key')

    except Exception:
        df = pd.DataFrame(columns=["Key","description","synonym"] )
        df1 = pd.DataFrame()
        df_min_max = pd.DataFrame()
    return df, df1, df_min_max

def get_timestamp_entities(r):
    """

    :param r:
    :return:
    """
    size = """SELECT count(*) FROM examination_date"""
    all_timestamp_entities = """ Select "Key","description","synonym" from name_type where type = 'timestamp' 
                                 order by "Key" """

    try:
        df = pd.read_sql(size, r)
        df = df.iloc[0]['count']

        df1 = pd.read_sql(all_timestamp_entities, r)
        df1 = df1.replace([None], ' ')



    except Exception:
        df = pd.DataFrame(columns=["Key","description","synonym"] )
        df1 = pd.DataFrame()
    return df, df1


def get_categorical_entities(r):
    """

    :param r: connection with database
    :return:
    """

    # Retrieve all categorical values
    examination_categorical_table_size = """SELECT count(*) FROM examination_categorical"""
    all_categorical_entities = """Select "Key","description" from name_type where "type" = 'String' order by "Key" """

    # Retrieve categorical values with subcategories
    all_subcategories = """Select distinct "Key","Value"[1] from examination_categorical order by "Key","Value"[1] """

    try:
        size = pd.read_sql(examination_categorical_table_size , r)
        df1 = size.iloc[0]['count']
        df2 = pd.read_sql(all_categorical_entities, r)
        df3 = pd.read_sql(all_subcategories, r)


        array = []
        # create dictionary with categories and subcategories
        for value in df2['Key']:
            df = {}
            df4 = df3[df3["Key"] == value]
            del df4['Key']
            df[value] = list(df4['Value'])
            array.append(df)

        df = dict(ChainMap(*array))

        return df1, df2, df,
    except Exception:
        array = []
        df1= pd.DataFrame()
        df = pd.DataFrame(columns=["Key","description"])
        df2 = dict(ChainMap(*array))
        return df1, df, df2


def get_measurement(r):
    """

    :param r:
    :return:
    """
    try:
        sql = """Select distinct "measurement":: int from examination order by "measurement" """
        df = pd.read_sql(sql, r)
        df['measurement'] = df['measurement'].astype(str)
        return df['measurement']
    except Exception:
        return ["No data"]


def number(r):
    """ Get number of all patients

     number use only for basic_stats
     """
    try:
        sql = """SELECT COUNT (*) FROM Patient"""
        n = pd.read_sql(sql, r)
        return n['count'], None
    except Exception:
        return None, "Problem with load data from database"


def patient(r):

    try:
        sql = """SELECT * FROM Patient"""
        df = pd.read_sql(sql, r)
        return df['Name_ID'], None
    except Exception:
        return None, "Problem with load data from database"


def get_unit(name, r):
    """ Get number of all patients

     number use only for basic_stats
     """
    try:
        sql = """SELECT "Key","unit" FROM name_type where "Key"='{}' """.format(name)
        df = pd.read_sql(sql, r)
        return df['unit'][0], None
    except Exception:
        return None, "Problem with load data from database"


def filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter):

    # case_id filter
    if case_id != None:
        case_id_all = "$$" + "$$,$$".join(case_id) + "$$"
        case_id_filter = """ SELECT "Name_ID" FROM patient where "Case_ID" in ({0}) """.format(case_id_all)

    # categorical_filter
    measurement_filteru = "$$" + "$$,$$".join(measurement_filter) + "$$"
    category_filter0=""
    numerical_filter0=""
    category_filter_where=""
    numerical_filter_where = ""

    for i in range(len(categorical)):
        cat = categorical_filter[i]
        cat = "$$"+cat[(cat.find(' is ') + 4):].replace(",", "$$,$$")+"$$"
        category_m = categorical[i].replace(" ","_")
        category_m0 = categorical[i - 1].replace(" ", "_")

        if i == 0:
            cat_filter = """Select {0}."Name_ID" FROM examination_categorical as {0}   """.format(category_m)

            cat_filter_where = """where {0}."Key"=$${1}$$ and {0}."Value"[1] in ({2}) and {0}.measurement in ({3}) """.format(category_m,
                                                                                                    categorical[i], cat,
                                                                                                    measurement_filteru)

        else:
            cat_filter = """ inner join examination_categorical as {0} on {1}."Name_ID" = {0}."Name_ID"  """.format(category_m, category_m0)

            cat_filter_where = """  and {3}."Key"=$${0}$$ and {3}."Value"[1] in ({1}) and {3}.measurement in ({2}) """.format(categorical[i], cat,
                                                                                                  measurement_filteru,
                                                                                                  category_m)

        category_filter0 = category_filter0 + cat_filter
        category_filter_where = category_filter_where + cat_filter_where
    category_filter = category_filter0 + category_filter_where


    for i in range(len(from1)):
        numeric_m =  numerical_filter_name[i].replace(" ","_")
        numeric_m0 = numerical_filter_name[i - 1].replace(" ", "_")
        if i == 0:
            num_filter = """Select {0}."Name_ID" FROM examination_numerical as {0}   """.format(numeric_m)

            num_filter_where = """where {0}."Key"=$${1}$$ and {0}."Value"[1] between $${2}$$ and $${3}$$ and {0}.measurement in ({4}) """.format(numeric_m,
                                                                                   numerical_filter_name[i], from1[i],
                                                                                   to1[i], measurement_filteru,)

        else:
            num_filter = """ inner join examination_numerical as {0} on {1}."Name_ID" = {0}."Name_ID"  """.format( numeric_m, numeric_m0)

            num_filter_where = """  and {4}."Key"=$${0}$$ and {4}."Value"[1] between $${1}$$ and $${2}$$ and {4}.measurement in ({3}) """.format(numerical_filter_name[i], from1[i],
                                                                                   to1[i], measurement_filteru,numeric_m)


        numerical_filter0 = numerical_filter0 + num_filter
        numerical_filter_where = numerical_filter_where + num_filter_where
    numerical_filter = numerical_filter0 + numerical_filter_where



    # join filters
    if categorical_filter and case_id and numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" inner join ({2}) AS c
        on b."Name_ID" = c."Name_ID" """.format(case_id_filter, category_filter, numerical_filter)
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


    return sql


def get_data(entity, what_table, measurement, case_id, categorical_filter, categorical, numerical_filter_name, from1,
             to1, measurement_filter, date, r):
    """
    Get data for tab Table browser
    get_numerical_values_basic_stats use in basic_stats

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,measurement,Key,instance,Value

    """

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    entity_column = '"'+'" text,"'.join(entity) + '" text'
    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Name_ID","measurement","Date","Key",array_to_string("Value",';') as "Value" 
                FROM examination_numerical 
                WHERE "Key" IN ({0})  and measurement IN ({1}) and "Date" Between '{2}' and '{3}'
                UNION
                SELECT "Name_ID","measurement","Date","Key",array_to_string("Value",';') as "Value"
                FROM examination_categorical 
                WHERE "Key" IN ({0}) and measurement IN ({1}) and "Date" Between '{2}' and '{3}'
                """.format(entity_final, measurement, date[0], date[1])

        sql2 = """SELECT * FROM crosstab('SELECT dense_rank() OVER (ORDER BY "measurement","Name_ID")::text AS 
                row_name,* from (Select "Name_ID","measurement","Date","Key",array_to_string("Value",'';'') as "Value" 
                FROM examination_numerical 
                WHERE  "Key" IN ({0})
                            UNION
                SELECT "Name_ID","measurement",
                "Date","Key",array_to_string("Value",'';'') as "Value" 
                FROM examination_categorical
                WHERE "Key" IN ({0})) as k  order by row_name',
                'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by "order"') 
                as ct (row_name text,"Name_ID" text,"measurement" text,"Date" text,{2}) 
                where "Date" Between '{3}' and '{4}' and "measurement" IN ({1}) order by "Name_ID", measurement 
                """.format(entity_final, measurement, entity_column, date[0], date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT en."Name_ID",en."measurement",en."Date",en."Key",array_to_string(en."Value",';') as "Value" 
                FROM examination_numerical as en 
                right join ({4}) as df 
                on en."Name_ID" = df."Name_ID"
                WHERE en."Key" IN ({0})  and en.measurement IN ({1}) and en."Date" Between '{2}' and '{3}' 
                UNION
                SELECT ec."Name_ID",ec."measurement",ec."Date",ec."Key",array_to_string(ec."Value",';') as "Value"
                FROM examination_categorical as ec 
                right join ({4}) as df 
                on ec."Name_ID" = df."Name_ID"
                WHERE ec."Key" IN ({0}) and ec.measurement IN ({1}) and ec."Date" Between '{2}' and '{3}' 
                """.format(entity_final, measurement, date[0], date[1], df)

        sql2 = """SELECT ek.* FROM crosstab(
                'SELECT dense_rank() OVER (ORDER BY "measurement","Name_ID")::text AS 
                row_name,* from (SELECT en."Name_ID",en."measurement",en."Date",en."Key",array_to_string(en."Value",'';'') as "Value" 
                FROM examination_numerical as en 
                right join ({5}) as df 
                on en."Name_ID" = df."Name_ID"
                WHERE en."Key" IN ({0}) 
                UNION
                SELECT ec."Name_ID",ec."measurement",ec."Date",ec."Key",array_to_string(ec."Value",'';'') as "Value"
                FROM examination_categorical as ec 
                right join ({5}) as df 
                on ec."Name_ID" = df."Name_ID"
                WHERE ec."Key" IN ({0}) ) as k order by row_name',
                'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by "order" ') 
                as ek (row_name text,"Name_ID" text,"measurement" text,"Date" text,{2}) 
                where "Date" Between '{3}' and '{4}' and "measurement" IN ({1}) 
                """.format(entity_final, measurement, entity_column, date[0], date[1], df)

    try:
        if what_table == 'long':
            df = pd.read_sql(sql, r)
        else:
            df = pd.read_sql(sql2, r)
            df = df.drop(['row_name'], axis=1)
        return df, None
    except Exception:
        df = pd.DataFrame()
        return df, "Problem with load data from database"


def get_num_values_basic_stats(entity, measurement, case_id, categorical_filter, categorical, numerical_filter_name,
                               from1, to1, measurement_filter, date, r):
    """
    Get numerical values from numerical table  from database

    get_numerical_values_basic_stats use in basic_stats

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,measurement,Key,instance,Value

    """
    round = 'not'
    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not case_id and not numerical_filter_name:
        if round == 'not':
            sql = """SELECT "Key","measurement",
                    count("Value"[1]),
                    min("Value"[1]),
                    max("Value"[1]),
                    AVG("Value"[1]) as "mean",
                    stddev("Value"[1]),
                    (stddev("Value"[1])/sqrt(count("Value"[1]))) as "stderr",
                    (percentile_disc(0.5) within group (order by "Value"[1])) as median 
                    FROM examination_numerical 
                    WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Date" between '{2}' and '{3}' 
                    group by "Key","measurement" order by "Key","measurement" """.format(
                    entity_final, measurement, date[0], date[1])
        else:
            sql = """SELECT "Key","measurement",
                    count("Value"[1]),
                    min("Value"[1]),
                    max("Value"[1]),
                    ROUND(AVG("Value"[1])::numeric,2) as "mean",
                    ROUND(stddev("Value"[1])::numeric,2),
                    ROUND((stddev("Value"[1])/sqrt(count("Value"[1])))::numeric,2) as "stderr",
                    (percentile_disc(0.5) within group (order by "Value"[1])) as median 
                    FROM examination_numerical
                    WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Date" between '{2}' and '{3}' 
                    group by "Key","measurement" order by "Key","measurement" """.format(
                    entity_final, measurement, date[0], date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        if round == 'not':
            sql = """SELECT "Key","measurement",
                    count("Value"[1]),
                    min("Value"[1]),
                    max("Value"[1]),
                    AVG("Value"[1]) as "mean",
                    stddev("Value"[1]),(stddev("Value"[1])/sqrt(count("Value"[1]))) as "stderr",
                    (percentile_disc(0.5) within group (order by "Value"[1])) as median 
                    FROM examination_numerical
                    WHERE "Key" IN ({0}) and "Name_ID" in ({4}) and "measurement" IN ({1}) 
                    and "Date" between '{2}' and '{3}' 
                    group by "Key","measurement" order by "Key","measurement"
                    """.format(entity_final, measurement, date[0], date[1],df)
        else:
            sql = """SELECT "Key","measurement",
                    count("Value"[1]),
                    min("Value"[1]),
                    max("Value"[1]),
                    ROUND(AVG("Value"[1])::numeric,2) as "mean",
                    ROUND(stddev("Value"[1])::numeric,2),
                    ROUND((stddev("Value"[1])/sqrt(count("Value"[1])))::numeric,2) as "stderr",
                    (percentile_disc(0.5) within group (order by "Value"[1])) as median 
                    FROM examination_numerical as en
                    left join ({4}) as df 
                    on en."Name_ID" = df."Name_ID" 
                    WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Date" between '{2}' and '{3}' 
                    group by "Key","measurement" order by "Key","measurement"
                    """.format(entity_final, measurement, date[0], date[1], df)

    try:
        df = pd.read_sql(sql, r)
        df = df.round(2)
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_cat_values_basic_stats(entity,measurement, case_id, categorical_filter, categorical, numerical_filter_name,
                               from1, to1, measurement_filter, date, r):
    """ Get number of categorical values from database

    get_cat_values_basic_stas use only for basic_stats categorical

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Key,count

    """

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"

    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Key","measurement",number,count("Key") 
                FROM examination_categorical,
                array_length("Value",1) as f (number) 
                WHERE "Key" IN ({0}) and "measurement" IN ({1}) 
                group by "measurement","Key",number """.format(entity_final, measurement)
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT "Key","measurement",number,count("Key") 
                FROM examination_categorical,
                array_length("Value",1) as f (number)
                WHERE "Key" IN ({0}) and "Name_ID" in ({4}) and "measurement" IN ({1}) 
                and "Date" between '{2}' and '{3}' 
                group by "measurement","Key",number """.format(entity_final, measurement, date[0], date[1], df)

    try:
        df = pd.read_sql(sql, r)
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_values_scatter_plot(x_entity, y_entity, x_measurement,y_measurement, case_id, categorical_filter, categorical,
                            numerical_filter_name, from1, to1, measurement_filter, date, r):
    """ Get numerical values from numerical table  from database

    get_values use in scatter plot, coplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity1,entity2,...

    """
    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Name_ID",AVG(f."Value") as "{0}" 
                FROM examination_numerical,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "measurement"= '{1}' and "Date" between '{2}' and '{3}' 
                Group by "Name_ID","measurement","Key" 
                order by "measurement"  """.format(x_entity, x_measurement, date[0], date[1])

        sql2 = """SELECT "Name_ID",AVG(f."Value") as "{0}" 
                FROM examination_numerical,
                unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "measurement"= '{1}' and "Date" between '{2}' and '{3}'
                Group by "Name_ID","measurement","Key" 
                order by "measurement" """.format(y_entity, y_measurement, date[0], date[1])

    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT en."Name_ID",AVG(f."Value") as "{0}" 
                FROM examination_numerical as en
                right join ({4}) as df 
                on en."Name_ID" = df."Name_ID" 
                ,unnest("Value") as f ("Value")  
                WHERE en."Key" IN ('{0}') and en."measurement"= '{1}' 
                and en."Date" between '{2}' and '{3}' 
                Group by en."Name_ID",en."measurement",en."Key" 
                order by en."measurement"  """.format(x_entity, x_measurement, date[0], date[1], df)

        sql2 = """SELECT en."Name_ID",AVG(f."Value") as "{0}" 
                FROM examination_numerical as en
                right join ({4}) as df 
                on en."Name_ID" = df."Name_ID" 
                ,unnest("Value") as f ("Value")  
                WHERE en."Key" IN ('{0}') and en."measurement"= '{1}' 
                and en."Date" between '{2}' and '{3}'
                Group by en."Name_ID",en."measurement",en."Key" 
                order by "measurement" """.format(y_entity, y_measurement, date[0], date[1], df)

    try:
        df3 = pd.read_sql(sql, r)
        df4 = pd.read_sql(sql2, r)
        return df3, df4, None
    except Exception:
        return None,None, "Problem with load data from database"


def get_cat_values(entity, subcategory, measurement, case_id, categorical_filter, categorical, numerical_filter_name,
                   from1, to1, measurement_filter, date, r):
    """ Get categorical values from database

    get_cat_values use in scatter plot and coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity

    """

    subcategory_final = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Name_ID",string_agg(distinct f."Value",',') FROM examination_categorical,
        unnest("Value") as f ("Value") 
        WHERE "Key"= '{0}' and f."Value" IN ({1})  and "measurement" IN ({2}) 
        Group by "Name_ID" 
        order by string_agg(distinct f."Value",',')""".format(entity, subcategory_final, measurement)

    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT ec."Name_ID",string_agg(distinct f."Value",',') FROM examination_categorical as ec
        right join ({3}) as df 
        on ec."Name_ID" = df."Name_ID",
        unnest("Value") as f ("Value") 
        WHERE ec."Key"= '{0}' and f."Value" IN ({1}) and ec."measurement" IN ({2}) 
        Group by ec."Name_ID" 
        order by string_agg(distinct f."Value",',')""".format(entity, subcategory_final, measurement, df)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return None, "The entity {} wasn't measured".format(entity)
    else:
        df.columns = ["Name_ID", entity]
        return df, None

def get_cat_values_histogram(entity, subcategory, measurement, case_id, categorical_filter, categorical, numerical_filter_name,
                   from1, to1, measurement_filter, date, r):
    """ Get categorical values from database

    get_cat_values use in scatter plot and coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity

    """

    subcategory_final = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Name_ID","measurement",string_agg(distinct f."Value",',') 
        FROM examination_categorical,
        unnest("Value") as f ("Value") 
        WHERE "Key"= '{0}' and f."Value" IN ({1})  and "measurement" IN ({2}) 
        Group by "Name_ID","measurement"
        order by string_agg(distinct f."Value",',')""".format(entity, subcategory_final, measurement)

    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT ec."Name_ID",ec."measurement",string_agg(distinct f."Value",',') 
        FROM examination_categorical as ec
        right join ({3}) as df 
        on ec."Name_ID" = df."Name_ID",
        unnest("Value") as f ("Value") 
        WHERE ec."Key"= '{0}' and f."Value" IN ({1}) and ec."measurement" IN ({2}) 
        Group by ec."Name_ID", ec."measurement"
        order by string_agg(distinct f."Value",',')""".format(entity, subcategory_final, measurement, df)

    df = pd.read_sql(sql, r)
    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return None, "The entity {} wasn't measured".format(entity)
    else:
        df.columns = ["Name_ID","measurement", entity]
        return df, None

def get_cat_values_barchart(entity, subcategory, measurement, case_id, categorical_filter, categorical,
                            numerical_filter_name, from1, to1, measurement_filter, date, r):
    """ Get number of subcategory values from database

    get_cat_values_barchart use only for barchart

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,Key,Value

    """

    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Value","measurement",count("Value") 
                FROM examination_categorical 
                WHERE "Key"='{0}' and "Date" BETWEEN '{3}' and '{4}'
                and "measurement" IN ({2}) and ARRAY{1} && "Value"  
                group by "Value","measurement" """.format(entity, subcategory, measurement, date[0], date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT "Value","measurement",count("Value") 
                FROM examination_categorical as ec
                right join ({5}) as df 
                on ec."Name_ID" = df."Name_ID"  
                WHERE "Key"='{0}' and "Date" BETWEEN '{3}' and '{4}'
                and "measurement" IN ({2}) and ARRAY{1} && "Value"  
                group by "Value","measurement" """.format(entity, subcategory, measurement, date[0], date[1], df)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return df, "{} not measured during this measurement".format(entity)
    else:
        a =lambda x: ','.join(x)
        df['Value'] = df['Value'].map(a)
        df.columns = [entity, 'measurement', 'count']
        return df, None


def get_num_cat_values(entity_num, entity_cat, subcategory, measurement, case_id, categorical_filter, categorical,
                       numerical_filter_name, from1, to1, measurement_filter, date, r):
    """ Retrieve categorical and numerical value

    get_num_cat_values use in histogram and boxplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity_num,entity_cat
     """
    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT en."Name_ID",en."measurement",
                AVG(a."Value") as "{0}",
                STRING_AGG(distinct f."Value", ',') as "{1}" 
                FROM examination_numerical as en 
                left join examination_categorical as ec 
                on en."Name_ID" = ec."Name_ID",
                unnest(en."Value") as a ("Value"),
                unnest(ec."Value") as f ("Value") 
                where en."Key" = '{0}' and ec."Key" = '{1}' and en."measurement" IN ({3}) and ec."measurement" IN ({3}) 
                and en."Date" Between '{4}' and '{5}' and f."Value" IN ({2}) 
                group by en."Name_ID",en."measurement",ec."measurement" order by en."Name_ID",en."measurement" 
                """.format(entity_num, entity_cat, subcategory, measurement,date[0],date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT en."Name_ID",en."measurement",
                AVG(a."Value") as "{0}",
                STRING_AGG(distinct f."Value", ',') as "{1}" 
                FROM examination_numerical as en 
                left join examination_categorical as ec 
                on en."Name_ID" = ec."Name_ID"
                right join ({6}) as df 
                on ec."Name_ID" = df."Name_ID"  
                ,unnest(en."Value") as a ("Value"),
                unnest(ec."Value") as f ("Value") 
                where en."Key" = '{0}' and ec."Key" = '{1}' and en."measurement" IN ({3}) and ec."measurement" IN ({3}) 
                and en."Date" Between '{4}' and '{5}' and f."Value" IN ({2}) 
                group by en."Name_ID",en."measurement",ec."measurement" order by en."Name_ID",en."measurement" 
                """.format(entity_num, entity_cat, subcategory, measurement, date[0], date[1], df)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return df, "The entity {0} or {1} wasn't measured".format(entity_num,entity_cat)
    else:
        return df, None


def get_values_heatmap(entity, measurement, case_id, categorical_filter, categorical, numerical_filter_name, from1,
                       to1, measurement_filter, date, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"

    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Name_ID","measurement","Key",AVG(f."Value") as "Value" 
                FROM examination_numerical, 
                unnest("Value") as f("Value") 
                WHERE "Key" IN ({0}) and "measurement" in ('{1}') and "Date" Between '{2}' and '{3}'
                Group by "Name_ID","measurement","Key" """.format(entity_fin, measurement, date[0], date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT en."Name_ID","measurement","Key",AVG(f."Value") as "Value" 
                FROM examination_numerical as en
                right join ({4}) as df 
                on en."Name_ID" = df."Name_ID" , 
                unnest("Value") as f("Value")
                WHERE "Key" IN ({0}) and "measurement" in ('{1}') and "Date" Between '{2}' and '{3}'
                Group by en."Name_ID","measurement","Key" """.format(entity_fin, measurement, date[0], date[1],df)

    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Name_ID"], columns="Key", values="Value", aggfunc=np.mean).reset_index()
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except Exception:
        return None, "Problem with load data from database"


def calculator(entity1, entity2, column_name, r):

    sql = """ SELECT a."Name_ID",a."measurement",
                DATE_PART('year',a."Value"::timestamp) - DATE_PART('year',b."Value"::timestamp) as "{2}" 
                FROM examination_date as a FULL JOIN examination_date as b on a."Name_ID" = b."Name_ID" 
                and a."measurement" = b."measurement" where a."Key"='{0}' and b."Key"='{1}' """.format(entity1, entity2, column_name)

    try:
        df = pd.read_sql(sql, r)
        return df
    except Exception:
        return None