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
        sql = """ Select min("Date"),max("Date") from examination """
        df = pd.read_sql(sql, r)
        start_date = datetime.strptime(df['min'][0], '%Y-%m-%d').timestamp() * 1000
        end_date = datetime.strptime(df['max'][0], '%Y-%m-%d').timestamp() * 1000
        return start_date, end_date
    except Exception:
        start_date = datetime.today().strftime('%Y-%m-%d').timestamp() * 1000
        end_date = datetime.today().strftime('%Y-%m-%d').timestamp() * 1000
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
        return df1,df, df2


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


def filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1):

    # case_id filter
    if case_id != None:
        case_id_all = "$$" + "$$,$$".join(case_id) + "$$"
        case_id_filter = """ SELECT "Name_ID" FROM patient where "Case_ID" in ({0}) """.format(case_id_all)

    # categorical_filter
    categorical_filter_str = [x.replace(" is ", "\" in ('").replace(",", "','") for x in categorical_filter]
    categorical_filter_str = '"' + "') and \"".join(categorical_filter_str) + "')"
    categorical_names = "$$" + "$$,$$".join(categorical) + "$$"
    categorical_columns = '"' + '" text,"'.join(categorical) + '" text'

    category_filter = """SELECT distinct "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0}) ')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str)

    #numerical_filter
    names = "$$" + "$$,$$".join(numerical_filter_name) + "$$"
    numerical_columns = '"' + '" double precision,"'.join(numerical_filter_name) + '" double precision'
    numerical = ""
    for i in range(len(from1)):
        if i == 0:
            numerical_filter = """ "{0}" between '{1}' and '{2}' """.format(numerical_filter_name[i],from1[i],to1[i])
        else:
            numerical_filter = """ and "{0}" between '{1}' and '{2}' """.format(numerical_filter_name[i], from1[i], to1[i])
        numerical = numerical + numerical_filter

    numerical_filter = """Select distinct "Name_ID" FROM crosstab('SELECT "Name_ID","Key",AVG(f."Value") as "Value" FROM 
                        examination_numerical, unnest("Value") as f("Value") WHERE "Key" IN ({0}) 
                        Group by "Name_ID","Key" ORDER  BY 1,2')  AS CT ("Name_ID" text,{1}) where {2}  """.format(names,numerical_columns,numerical)

    # join filters
    if categorical_filter and case_id and numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" inner join ({2}) AS c
        on b."Name_ID" = c."Name_ID" """.format(case_id_filter, category_filter, numerical_filter)
    elif not case_id and categorical_filter and numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" """.format(
            category_filter, numerical_filter)
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


def get_data(entity, what_table, case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, date, r):
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

    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Name_ID","measurement","Key",array_to_string("Value",';') as "Value" 
                FROM examination_numerical 
                WHERE "Key" IN ({0})  and "Date" Between '{1}' and '{2}'
                UNION
                SELECT "Name_ID","measurement","Key",array_to_string("Value",';') as "Value"
                FROM examination_categorical 
                WHERE "Key" IN ({0}) and "Date" Between '{1}' and '{2}'
                """.format(entity_final,date[0],date[1])

        sql2 = """SELECT * FROM crosstab('SELECT dense_rank() OVER (ORDER BY "measurement","Name_ID")::text AS 
                row_name,"Name_ID","measurement","Date","Key",array_to_string("Value",'';'') as "Value" 
                FROM examination_numerical 
                WHERE  "Key" IN ({0}) 
                            UNION
                SELECT dense_rank() OVER (ORDER BY "measurement","Name_ID")::text AS row_name,"Name_ID","measurement",
                "Date","Key",array_to_string("Value",'';'') as "Value" 
                FROM examination_categorical
                WHERE "Key" IN ({0})  order by row_name',
                'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by "order"') 
                as ct (row_name text,"Name_ID" text,"measurement" text,"Date" text,{1}) 
                where "Date" Between '{2}' and '{3}' order by "Name_ID", measurement """.format(entity_final, entity_column, date[0], date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1)
        sql = """SELECT en."Name_ID",en."measurement",en."Key",array_to_string(en."Value",';') as "Value" 
                FROM examination_numerical as en 
                right join ({3}) as df 
                on en."Name_ID" = df."Name_ID" 
                WHERE en."Key" IN ({0})  and en."Date" Between '{1}' and '{2}' 
                UNION
                SELECT ec."Name_ID",ec."measurement",ec."Key",array_to_string(ec."Value",';') as "Value"
                FROM examination_categorical as ec 
                right join ({3}) as df 
                on ec."Name_ID" = df."Name_ID"
                WHERE ec."Key" IN ({0}) and ec."Date" Between '{1}' and '{2}' 
                """.format(entity_final, date[0], date[1], df)

        sql2 = """SELECT ec.* FROM crosstab(
                'SELECT dense_rank() OVER (ORDER BY "Name_ID","measurement")::text AS row_name,
                "Name_ID","measurement","Date","Key",array_to_string("Value",'';'') as "Value" 
                FROM examination_numerical 
                WHERE  "Key" IN ({0}) 
                            UNION
                SELECT dense_rank() OVER (ORDER BY "Name_ID","measurement")::text AS row_name,
                "Name_ID","measurement","Date","Key",array_to_string("Value",'';'') as "Value" 
                FROM examination_categorical
                WHERE "Key" IN ({0})  order by row_name',
                'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by "order"') 
                as ec (row_name text,"Name_ID" text,"measurement" text,"Date" text,{1}) 
                right join ({4}) as df 
                on ec."Name_ID" = df."Name_ID"  
                where "Date" Between '{2}' and '{3}' """.format(entity_final, entity_column, date[0], date[1], df)


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
                               from1, to1, date, r):
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
            sql = """SELECT "Key","measurement","instance",
                    count(f."Value"),
                    min(f."Value"),
                    max(f."Value"),
                    AVG(f."Value") as "mean",
                    stddev(f."Value"),
                    (stddev(f."Value")/sqrt(count(f."Value"))) as "stderr",
                    (percentile_disc(0.5) within group (order by f."Value")) as median 
                    FROM examination_numerical,unnest("Value") WITH ordinality as f ("Value", instance) 
                    WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Date" between '{2}' and '{3}' 
                    group by "Key","measurement","instance" order by "Key","measurement","instance" """.format(
                    entity_final, measurement, date[0], date[1])
        else:
            sql = """SELECT "Key","measurement","instance",
                    count(f."Value"),
                    min(f."Value"),
                    max(f."Value"),
                    ROUND(AVG(f."Value")::numeric,2) as "mean",
                    ROUND(stddev(f."Value")::numeric,2),
                    ROUND((stddev(f."Value")/sqrt(count(f."Value")))::numeric,2) as "stderr",
                    (percentile_disc(0.5) within group (order by f."Value")) as median 
                    FROM examination_numerical,unnest("Value") WITH ordinality as f ("Value", instance) 
                    WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Date" between '{2}' and '{3}' 
                    group by "Key","measurement","instance" order by "Key","measurement","instance" """.format(
                    entity_final, measurement, date[0], date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1)

        if round == 'not':
            sql = """SELECT "Key","measurement","instance",
                    count(f."Value"),
                    min(f."Value"),
                    max(f."Value"),
                    AVG(f."Value") as "mean",
                    stddev(f."Value"),(stddev(f."Value")/sqrt(count(f."Value"))) as "stderr",
                    (percentile_disc(0.5) within group (order by f."Value")) as median 
                    FROM examination_numerical,unnest("Value") WITH ordinality as f ("Value", instance)
                    WHERE "Key" IN ({0}) and "Name_ID" in ({4}) and "measurement" IN ({1}) 
                    and "Date" between '{2}' and '{3}' 
                    group by "Key","measurement","instance" order by "Key","measurement","instance"
                    """.format(entity_final, measurement, date[0], date[1],df)
        else:
            sql = """SELECT "Key","measurement","instance",
                    count(f."Value"),
                    min(f."Value"),
                    max(f."Value"),
                    ROUND(AVG(f."Value")::numeric,2) as "mean",
                    ROUND(stddev(f."Value")::numeric,2),
                    ROUND((stddev(f."Value")/sqrt(count(f."Value")))::numeric,2) as "stderr",
                    (percentile_disc(0.5) within group (order by f."Value")) as median 
                    FROM examination_numerical as en,unnest("Value") WITH ordinality as f ("Value", instance) 
                    left join ({4}) as df 
                    on en."Name_ID" = df."Name_ID" 
                    WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Date" between '{2}' and '{3}' 
                    group by "Key","measurement","instance" order by "Key","measurement","instance" 
                    """.format(entity_final, measurement, date[0], date[1], df)


    try:
        df = pd.read_sql(sql, r)
        df = df.round(2)
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_cat_values_basic_stats(entity,measurement, case_id, categorical_filter, categorical, numerical_filter_name,
                               from1, to1, date, r):
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
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1)
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
                            numerical_filter_name, from1, to1, date, r):
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
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1)
        sql = """SELECT "Name_ID",AVG(f."Value") as "{0}" 
                FROM examination_numerical
                ,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "Name_ID" in ({4}) and "measurement"= '{1}' 
                and "Date" between '{2}' and '{3}' 
                Group by "Name_ID","measurement","Key" 
                order by "measurement"  """.format(x_entity, x_measurement, date[0], date[1], df)

        sql2 = """SELECT "Name_ID",AVG(f."Value") as "{0}" 
                FROM examination_numerical
                ,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "Name_ID" in ({4}) and "measurement"= '{1}' 
                and "Date" between '{2}' and '{3}'
                Group by "Name_ID","measurement","Key" 
                order by "measurement" """.format(y_entity, y_measurement, date[0], date[1], df)
    df3 = pd.read_sql(sql, r)
    df4 = pd.read_sql(sql2, r)
    try:
        df3 = pd.read_sql(sql, r)
        df4 = pd.read_sql(sql2, r)

        if len(df3) == 0:
            error = "Category {} is empty".format(x_entity)
            return None, error
        elif len(df4) == 0:
            error = "Category {} is empty".format(y_entity)
            return None, error
        else:
            df = df3.merge(df4, on=["Name_ID"])
            return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_cat_values(entity, subcategory, measurement, case_id, categorical_filter, categorical, numerical_filter_name,
                   from1, to1, date, r):
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
        sql = """SELECT "Name_ID",string_agg(distinct f."Value",',') 
        FROM examination_categorical,
        unnest("Value") as f ("Value") 
        WHERE "Key"= '{0}' and f."Value" IN ({1})  and "measurement" IN ({2}) 
        Group by "Name_ID" 
        order by string_agg(distinct f."Value",',')""".format(entity, subcategory_final, measurement)

    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, r)
        sql = """SELECT "Name_ID",string_agg(distinct f."Value",',') 
        FROM examination_categorical
        right join ({3}) as df 
        on ec."Name_ID" = df."Name_ID",
        unnest("Value") as f ("Value") 
        WHERE "Key"= '{0}' and f."Value" IN ({1}) and "measurement" IN ({2}) 
        Group by "Name_ID" 
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


def get_cat_values_barchart(entity, subcategory, measurement, case_id, categorical_filter, categorical,
                            numerical_filter_name, from1, to1, date, r):
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
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1)
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
        df['Value']=df['Value'].map(a)
        df.columns = [entity,'measurement', 'count']
        return df,None


def get_num_cat_values(entity_num, entity_cat, subcategory, measurement, case_id, categorical_filter, categorical,
                       numerical_filter_name, from1, to1, date, r):
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
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1)
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
                       to1, date, r):
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
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1)
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



