import pandas as pd
import numpy as np
import datetime
import time
from collections import ChainMap


def get_header(r):
    """
    :param r: connection with database
    :return: data from header table
    """
    try:
        sql = "SELECT * FROM header"
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
        sql = """ SELECT min("Date"),max("Date") FROM examination_numerical """
        df = pd.read_sql(sql, r)
        start_date = datetime.datetime.strptime(df['min'][0], '%Y-%m-%d').timestamp() * 1000
        end_date = datetime.datetime.strptime(df['max'][0], '%Y-%m-%d').timestamp() * 1000
    except Exception:
        now = datetime.datetime.now()
        start_date = datetime.datetime.timestamp(now - datetime.timedelta(days=365.24*100)) * 1000
        end_date = datetime.datetime.timestamp(now) * 1000
    return start_date, end_date


def get_entities(r):
    """
    :param r: connection with database
    :return: DataFrame with entities names and their description
            DataFrame with entities which should be showed on first page
    """
    all_entities = """SELECT "Key","description","synonym" FROM name_type ORDER BY "order" """
    show_on_first_page = """SELECT "Key" FROM name_type WHERE "show" = '+' """

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
    all_numerical_entities = """SELECT "Key","description","synonym" FROM name_type WHERE type = 'Double' \
                                ORDER BY "Key" """
    min_max = """SELECT "Key",max("Value"),min("Value") FROM examination_numerical GROUP BY "Key" """

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
    """ """
    size = """SELECT count(*) FROM examination_date"""
    all_timestamp_entities = """ SELECT "Key","description","synonym" FROM name_type WHERE type = 'timestamp' 
                                 ORDER BY "Key" """

    try:
        df = pd.read_sql(size, r)
        df = df.iloc[0]['count']

        df1 = pd.read_sql(all_timestamp_entities, r)
        df1 = df1.replace([None], ' ')

    except Exception:
        df = pd.DataFrame(columns=["Key", "description", "synonym"])
        df1 = pd.DataFrame()
    return df, df1


def get_categorical_entities(r):
    """

    :param r: connection with database
    :return:
    """

    # Retrieve all categorical values
    examination_categorical_table_size = """SELECT count(*) FROM examination_categorical"""
    all_categorical_entities = """SELECT "Key","description" FROM name_type WHERE "type" = 'String' ORDER BY "Key" """

    # Retrieve categorical values with subcategories
    all_subcategories = """SELECT DISTINCT "Key","Value" FROM examination_categorical ORDER by "Key","Value" """ # check if group by is faster but shouldn't

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
        sql = """SELECT DISTINCT "measurement":: int FROM examination ORDER BY "measurement" """ # add the information about measurents to other table MAYBE
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
        sql = """SELECT "Key","unit" FROM name_type WHERE "Key"='{}' """.format(name)
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
    category_filter0 = ""
    numerical_filter0 = ""
    category_filter_where = ""
    numerical_filter_where = ""

    for i in range(len(categorical)):
        cat = categorical_filter[i]
        cat = "$$"+cat[(cat.find(' is ') + 4):].replace(",", "$$,$$")+"$$"
        category_m = categorical[i].replace(" ", "_")
        category_m0 = categorical[i - 1].replace(" ", "_")

        if i == 0:
            cat_filter = """SELECT {0}."Name_ID" FROM examination_categorical AS {0}   """.format(category_m)

            cat_filter_where = """WHERE {0}."Key"=$${1}$$ AND {0}."Value" IN ({2}) AND {0}.measurement IN ({3}) """\
                .format(category_m, categorical[i], cat, measurement_filteru)

        else:
            cat_filter = """ INNER JOIN examination_categorical AS {0} ON {1}."Name_ID" = {0}."Name_ID" """\
                .format(category_m, category_m0)

            cat_filter_where = """  AND {3}."Key"=$${0}$$ AND {3}."Value" IN ({1}) AND {3}.measurement IN ({2}) """\
                .format(categorical[i], cat,measurement_filteru, category_m)

        case_cat = """ WHEN "Key"=$${0}$$ and "Value" IN ({1}) AND measurement IN ({2}) THEN "Name_ID" """\
            .format(categorical[i], cat, measurement_filteru)

        category_filter0 = category_filter0 + cat_filter
        category_filter_where = category_filter_where + cat_filter_where
    category_filter = category_filter0 + category_filter_where

    case_cat_final = """ SELECT "Name_ID",count("Name_ID")
                         FROM (SELECT CASE {0} END AS "Name_ID" FROM examination_categorical) f 
                         GROUP BY "Name_ID" 
                         HAVING count("Name_ID") = {1} """.format(case_cat, len(categorical))



    """ SELECT "Name_ID1" from (SELECT CASE WHEN "Key"=$$Diabetes$$ and "Value"[1] IN ('no') AND measurement 
    IN ('1') THEN "Name_ID" END AS "Name_ID1",CASE WHEN "Key"=$$NYHA$$ and "Value"[1] IN ('I','II') 
    AND measurement IN ('1') THEN "Name_ID" END AS "Name_ID2" FROM examination_categorical 
    where examination_categorical is not null) f group by "Name_ID1" """

    for i in range(len(from1)):
        numeric_m = numerical_filter_name[i].replace(" ", "_")
        numeric_m0 = numerical_filter_name[i - 1].replace(" ", "_")
        if i == 0:
            num_filter = """SELECT {0}."Name_ID" FROM examination_numerical as {0}   """.format(numeric_m)

            num_filter_where = """WHERE {0}."Key"=$${1}$$ AND {0}."Value" BETWEEN $${2}$$ AND $${3}$$ 
                                    AND {0}.measurement IN ({4}) """.format(numeric_m, numerical_filter_name[i],
                                                                            from1[i], to1[i], measurement_filteru)

        else:
            num_filter = """ INNER JOIN examination_numerical as {0} 
                             ON {1}."Name_ID" = {0}."Name_ID"  """.format(numeric_m, numeric_m0)

            num_filter_where = """ AND {4}."Key"=$${0}$$ 
                                   AND {4}."Value" BETWEEN $${1}$$ AND $${2}$$ 
                                   AND {4}.measurement IN ({3}) """.format(numerical_filter_name[i], from1[i], to1[i],
                                                                           measurement_filteru,numeric_m)
        case_num = """ WHEN "Key"=$${0}$$ and "Value" BETWEEN $${1}$$ AND $${2}$$ AND measurement IN ({2}) 
                       THEN "Name_ID" """.format(numerical_filter_name[i], from1[i], to1[i], measurement_filteru)

        numerical_filter0 = numerical_filter0 + num_filter
        numerical_filter_where = numerical_filter_where + num_filter_where
    numerical_filter = numerical_filter0 + numerical_filter_where

    case_num_final = """ SELECT "Name_ID",count("Name_ID")
                         FROM (SELECT CASE {0} END AS "Name_ID" FROM examination_categorical) f 
                         GROUP BY "Name_ID" 
                         HAVING count("Name_ID") = {1} """.format(case_num, len(from1))

    print(case_num_final)
    print(numerical_filter)

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
    """ Get DataFrame with selected values to plot scatter plot  """

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    entity_column = '"'+'" text,"'.join(entity) + '" text'
    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Name_ID","measurement","Date","Key","Value"::text 
                FROM examination_numerical 
                WHERE "Key" IN ({0})  
                AND measurement IN ({1}) 
                AND "Date" BETWEEN '{2}' AND '{3}'
                UNION
                SELECT "Name_ID","measurement","Date","Key","Value"
                FROM examination_categorical 
                WHERE "Key" IN ({0}) 
                AND measurement IN ({1}) 
                ANd "Date" BETWEEN '{2}' and '{3}'
                """.format(entity_final, measurement, date[0], date[1])

        sql2 = """SELECT * FROM crosstab('SELECT dense_rank() OVER (ORDER BY "measurement","Name_ID")::text AS row_name,* 
                                        FROM (SELECT "Name_ID","measurement","Date","Key",
                                                        STRING_AGG("Value"::text,'';'') "Value"
                                                FROM examination_numerical 
                                                WHERE  "Key" IN ({0})
                                                GROUP BY "Name_ID","measurement","Date","Key"
                                                UNION
                                            SELECT "Name_ID","measurement","Date","Key",STRING_AGG("Value",'';'') "Value"
                                            FROM examination_categorical
                                            WHERE "Key" IN ({0})
                                            GROUP BY "Name_ID","measurement","Date","Key"
                                            ) AS k  
                                            ORDER BY row_name',
                                        'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) ORDER BY "order"') 
                                        AS ct (row_name text,"Name_ID" text,"measurement" text,"Date" text,{2}) 
                WHERE "Date" BETWEEN '{3}' AND '{4}' 
                AND "measurement" IN ({1}) 
                ORDER BY "Name_ID", measurement 
                """.format(entity_final, measurement, entity_column, date[0], date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT en."Name_ID",en."measurement",en."Date",en."Key",array_to_string(en."Value",';') as "Value" 
                FROM examination_numerical as en 
                RIGHT JOIN ({4}) AS df 
                ON en."Name_ID"=df."Name_ID"
                WHERE en."Key" IN ({0}) 
                AND en.measurement IN ({1}) 
                AND en."Date" BETWEEN '{2}' AND '{3}' 
                UNION
                SELECT ec."Name_ID",ec."measurement",ec."Date",ec."Key",array_to_string(ec."Value",';') as "Value"
                FROM examination_categorical as ec 
                RIGHT JOIN ({4}) as df 
                on ec."Name_ID"=df."Name_ID"
                WHERE ec."Key" IN ({0}) 
                AND ec.measurement IN ({1}) 
                AND ec."Date" BETWEEN '{2}' AND '{3}' 
                """.format(entity_final, measurement, date[0], date[1], df)

        sql2 = """SELECT ek.* FROM crosstab('SELECT dense_rank() OVER (ORDER BY "measurement","Name_ID")::text AS row_name,*
                                            FROM (SELECT en."Name_ID",en."measurement",en."Date",en."Key",
                                                             STRING_AGG("Value"::text,'';'') "Value"
                                                    FROM examination_numerical AS en 
                                                    RIGHT JOIN ({5}) AS df 
                                                    ON en."Name_ID"=df."Name_ID"
                                                    WHERE en."Key" IN ({0})
                                                    GROUP BY "Name_ID","measurement","Date","Key" 
                                                    UNION
                                                SELECT ec."Name_ID",ec."measurement",ec."Date",ec."Key",
                                                        STRING_AGG("Value",'';'') "Value"
                                                FROM examination_categorical AS ec 
                                                RIGHT JOIN ({5}) AS df 
                                                ON ec."Name_ID" = df."Name_ID"
                                                WHERE ec."Key" IN ({0}) 
                                                GROUP BY "Name_ID","measurement","Date","Key"
                                                ) as k ORDER BY row_name',
                                            'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) ORDER BY "order" ') 
                                            AS ek (row_name text,"Name_ID" text,"measurement" text,"Date" text,{2}) 
                    WHERE "Date" BETWEEN '{3}' AND '{4}' AND "measurement" IN ({1}) 
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


def get_basic_stats(entity, measurement, case_id, categorical_filter, categorical, numerical_filter_name, from1, to1,
                    measurement_filter, date, r):
    """ """

    round = 'not'
    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not case_id and not numerical_filter_name:
        if round == 'not':
            sql = """SELECT "Key","measurement",
                    count(DISTINCT "Name_ID"),
                    min("Value"),
                    max("Value"),
                    AVG("Value") AS "mean",
                    stddev("Value"),
                    (stddev("Value")/sqrt(count("Value"))) AS "stderr",
                    (percentile_disc(0.5) within group (order by "Value")) AS median 
                    FROM examination_numerical 
                    WHERE "Key" IN ({0}) 
                    AND "measurement" IN ({1}) 
                    AND "Date" BETWEEN '{2}' AND '{3}' 
                    GROUP BY "Key","measurement" 
                    ORDER BY "Key","measurement" """.format(
                    entity_final, measurement, date[0], date[1])
        else:
            sql = """SELECT "Key","measurement",
                    count(DISTINCT "Name_ID"),
                    min("Value"),
                    max("Value"),
                    ROUND(AVG("Value")::numeric,2) AS "mean",
                    ROUND(stddev("Value")::numeric,2),
                    ROUND((stddev("Value")/sqrt(count("Value")))::numeric,2) AS "stderr",
                    (percentile_disc(0.5) within group (order by "Value")) as median 
                    FROM examination_numerical
                    WHERE "Key" IN ({0}) 
                    AND "measurement" IN ({1}) 
                    AND "Date" BETWEEN '{2}' AND '{3}' 
                    GROUP BY "Key","measurement" 
                    ORDER BY "Key","measurement" """.format(
                    entity_final, measurement, date[0], date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        if round == 'not':
            sql = """SELECT "Key","measurement",
                    count(DISTINCT "Name_ID"),
                    min("Value"),
                    max("Value"),
                    AVG("Value") AS "mean",
                    stddev("Value"),(stddev("Value")/sqrt(count("Value"))) AS "stderr",
                    (percentile_disc(0.5) within group (order by "Value")) AS median 
                    FROM examination_numerical
                    WHERE "Key" IN ({0}) 
                    AND "Name_ID" IN ({4}) 
                    AND "measurement" IN ({1}) 
                    AND "Date" BETWEEN '{2}' AND '{3}' 
                    GROUP BY "Key","measurement" 
                    ORDER BY "Key","measurement"
                    """.format(entity_final, measurement, date[0], date[1],df)
        else:
            sql = """SELECT "Key","measurement",
                    count(DISTINCT "Name_ID"),
                    min("Value"),
                    max("Value"),
                    ROUND(AVG("Value")::numeric,2) AS "mean",
                    ROUND(stddev("Value")::numeric,2),
                    ROUND((stddev("Value")/sqrt(count("Value")))::numeric,2) AS "stderr",
                    (percentile_disc(0.5) within group (order by "Value")) AS median 
                    FROM examination_numerical AS en
                    RIGHT JOIN ({4}) AS df 
                    ON en."Name_ID" = df."Name_ID" 
                    WHERE "Key" IN ({0}) 
                    AND "measurement" IN ({1}) 
                    AND "Date" between '{2}' and '{3}' 
                    GROUP BY "Key","measurement" 
                    ORDER BY "Key","measurement"
                    """.format(entity_final, measurement, date[0], date[1], df)

    try:
        df = pd.read_sql(sql, r)
        df = df.round(2)
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_cat_basic_stats(entity, measurement, case_id, categorical_filter, categorical, numerical_filter_name, from1,
                        to1, measurement_filter, date, r):
    """ """

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"

    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Key","measurement",count(DISTINCT "Name_ID") 
                FROM examination_categorical
                WHERE "Key" IN ({0}) 
                AND "measurement" IN ({1}) 
                GROUP BY "measurement","Key" """.format(entity_final, measurement)
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT "Key","measurement",count(DISTINCT "Name_ID") 
                FROM examination_categorical
                WHERE "Key" IN ({0}) 
                AND "Name_ID" in ({4}) 
                AND "measurement" IN ({1}) 
                AND "Date" BETWEEN '{2}' AND '{3}' 
                GROUP BY "Name_ID","measurement","Key" """.format(entity_final, measurement, date[0], date[1], df)

    try:
        df = pd.read_sql(sql, r)
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_scatter_plot(entity, subcategory, x_entity, y_entity, x_measurement,y_measurement, case_id, categorical_filter,
                     categorical, numerical_filter_name, from1, to1, measurement_filter, date, r):
    """ Get DataFrame with selected values to plot scatter plot """

    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Name_ID",AVG("Value") as "{0}" 
                FROM examination_numerical  
                WHERE "Key" IN ('{0}') 
                AND "measurement"='{1}' 
                AND "Date" BETWEEN '{2}' AND '{3}' 
                GROUP BY "Name_ID" """.format(x_entity, x_measurement, date[0], date[1])

        sql2 = """SELECT "Name_ID",AVG("Value") as "{0}" 
                FROM examination_numerical
                WHERE "Key" IN ('{0}') 
                AND "measurement"= '{1}' AND "Date" BETWEEN '{2}' AND '{3}'
                GROUP BY "Name_ID" """.format(y_entity, y_measurement, date[0], date[1])

        # join or case what is faster?
        sql_test = """SELECT x."Name_ID",AVG(x."Value") as "{0}",AVG(y."Value") as "{0}"{,ec."Value"}
                        FROM examination_numerical as "x"
                        INNER JOIN examination_numerical as "y"
                            ON x."Name_ID" == y."Name_ID"
                        {INNER JOIN examination_categorical AS ec
                        ON y."Name_ID" = ec."Name_ID"}  
                        WHERE x."Key" IN ('{0}') 
                        AND x."measurement"='{1}' 
                        AND y."measurement"='{1}' 
                        AND x."Date" BETWEEN '{2}' AND '{3}' 
                        AND y."Date" BETWEEN '{2}' AND '{3}'
                        {AND ec."Key"= '{0}' 
                        AND ec."Value" IN ({1})}  
                        GROUP BY x."Name_ID",y."Name_ID"  """

        # categorical value
        sql = """SELECT "Name_ID","Value" FROM examination_categorical,
                 WHERE "Key"= '{0}' 
                 AND "Value" IN ({1}) """.format(entity, subcategory)


    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT en."Name_ID",AVG("Value") as "{0}" 
                FROM examination_numerical as en
                RIGHT JOIN ({4}) as df 
                ON en."Name_ID" = df."Name_ID" 
                WHERE en."Key" IN ('{0}') 
                AND en."measurement"= '{1}' 
                AND en."Date" BETWEEN '{2}' AND '{3}' 
                GROUP BY en."Name_ID",en."measurement",en."Key" 
                ORDER BY en."measurement"  """.format(x_entity, x_measurement, date[0], date[1], df)

        sql2 = """SELECT en."Name_ID",AVG("Value") as "{0}" 
                FROM examination_numerical as en
                RIGHT JOIN ({4}) as df 
                ON en."Name_ID" = df."Name_ID" 
                WHERE en."Key" IN ('{0}') 
                AND en."measurement"= '{1}' 
                AND en."Date" BETWEEN '{2}' AND '{3}'
                GROUP BY en."Name_ID",en."measurement",en."Key" 
                ORDER BY "measurement" """.format(y_entity, y_measurement, date[0], date[1], df)

    try:
        df3 = pd.read_sql(sql, r)
        df4 = pd.read_sql(sql2, r)
        df = df3.merge(df4, on=["Name_ID"])
        return df, None
    except Exception:
        return None, None, "Problem with load data from database"


def get_bar_chart(entity, subcategory, measurement, case_id, categorical_filter, categorical,numerical_filter_name,
                  from1, to1, measurement_filter, date, r):
    """ Get DataFrame with selected values to plot bar chart """

    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"

    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Value" AS "{0}","measurement",count("Value")
                FROM examination_categorical 
                WHERE "Key"='{0}'
                AND "Value" IN ({1}) 
                AND "Date" BETWEEN '{3}' AND '{4}'
                AND "measurement" IN ({2})
                GROUP BY "Value","measurement" """.format(entity, subcategory, measurement, date[0], date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT "Value" AS "{0}","measurement",count("Value") 
                FROM examination_categorical AS ec
                RIGHT JOIN ({5}) as df 
                ON ec."Name_ID" = df."Name_ID"  
                WHERE "Key"='{0}'
                AND "Value" IN ({1})  
                AND "Date" BETWEEN '{3}' AND '{4}'
                AND "measurement" IN ({2})
                GROUP BY "Value","measurement" """.format(entity, subcategory, measurement, date[0], date[1], df)

    try:
        df = pd.read_sql(sql, r)
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_histogram_box_plot(entity_num, entity_cat, subcategory, measurement, case_id, categorical_filter, categorical,
                           numerical_filter_name, from1, to1, measurement_filter, date, r):
    """ Get DataFrame with selected values to plot histogram or box plot """
    
    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT en."Name_ID",en."measurement",AVG(en."Value") AS "{0}",ec."Value" AS "{1}"
                FROM examination_numerical AS en 
                LEFT JOIN examination_categorical AS ec 
                ON en."Name_ID" = ec."Name_ID"
                WHERE en."Key" = '{0}' 
                AND ec."Key" = '{1}' 
                AND ec."Value" IN ({2}) 
                AND en."measurement" IN ({3}) 
                AND en."Date" BETWEEN '{4}' AND '{5}'
                GROUP BY en."Name_ID",en."measurement",ec."Value" 
                """.format(entity_num, entity_cat, subcategory, measurement,date[0],date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT en."Name_ID",en."measurement",AVG(en."Value") AS "{0}",ec."Value" AS "{1}" 
                FROM examination_numerical AS en 
                LEFT JOIN examination_categorical AS ec 
                ON en."Name_ID" = ec."Name_ID"
                RIGHT JOIN ({6}) as df 
                ON ec."Name_ID" = df."Name_ID"
                WHERE en."Key" = '{0}' 
                AND ec."Key" = '{1}'
                AND ec."Value" IN ({2})  
                AND en."measurement" IN ({3}) 
                AND en."Date" BETWEEN '{4}' and '{5}' 
                GROUP BY en."Name_ID",en."measurement",ec."Value"
                """.format(entity_num, entity_cat, subcategory, measurement, date[0], date[1], df)

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return df, "The entity {0} or {1} wasn't measured".format(entity_num, entity_cat)
    else:
        return df, None


def get_heat_map(entity, case_id, categorical_filter, categorical, numerical_filter_name, from1,
                       to1, measurement_filter, date, r):
    """ Get DataFrame with selected values to plot heat map"""

    case_statement = ""
    crosstab_columns = ""
    for ent in entity:
        create_case_statement = """CASE WHEN "Key" = '{0}' THEN "Value" END AS "{0}" """.format(ent)
        case_statement = case_statement + ',' + create_case_statement
        create_crosstab_columns = '"{}" double precision'.format(ent)
        crosstab_columns = crosstab_columns + ',' + create_crosstab_columns

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"

    if not categorical_filter and not case_id and not numerical_filter_name:
        sql = """SELECT "Name_ID","Key",AVG("Value") as "Value" 
                FROM examination_numerical 
                WHERE "Key" IN ({0}) 
                AND "Date" BETWEEN '{1}' AND '{2}'
                GROUP BY "Name_ID","Key" """.format(entity_fin, date[0], date[1])
    else:
        df = filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter)
        sql = """SELECT en."Name_ID","Key","Value" 
                FROM examination_numerical AS en
                RIGHT JOIN ({3}) AS df 
                ON en."Name_ID" = df."Name_ID" 
                WHERE "Key" IN ({0}) 
                AND "Date" Between '{1}' AND '{2}'
                GROUP BY en."Name_ID","Key" """.format(entity_fin, date[0], date[1], df)

    sql_case = """SELECT "Name_ID","Key",AVG(f."Value") as "Value", {3}
            FROM examination_numerical 
            WHERE "Key" IN ({0}) 
            AND "Date" BETWEEN '{1}' ANd '{2}'
            GROUP BY "Name_ID" """.format(entity_fin, date[0], date[1],case_statement)

    sql_crosstab = """SELECT * FROM crosstab ('SELECT "Name_ID","Key","Value" 
            FROM examination_numerical 
            WHERE "Key" IN ({0}) 
            AND "Date" BETWEEN '{1}' ANd '{2}'
            ORDER  BY 1,2') AS ct ("Name_ID" text, {3})""".format(entity_fin, date[0], date[1], crosstab_columns)

    print(sql_case)
    print(sql_crosstab)

    try:
        start_time = time.time()
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Name_ID"], columns="Key", values="Value", aggfunc=np.mean).reset_index() # should I do this sql?
        print("--- %s seconds ---" % (time.time() - start_time))
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