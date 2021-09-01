import pandas as pd
import numpy as np
from datetime import datetime
from collections import ChainMap


def get_header(r):
    """
    :param r: connection with database
    :return: DataFrame with header for table browser
    """
    try:
        sql = "Select * from header"
        df = pd.read_sql(sql, r)
        return df
    except Exception:
        return ["No data"]


def get_date(r):
    """
    :param r: connection with database
    :return: DataFrame with header for table browser
    """
    try:
        sql = """ Select min("Date"),max("Date") from examination_numerical """
        df = pd.read_sql(sql, r)
        start_date,end_date = datetime.strptime(df['min'][0], '%Y-%m-%d').timestamp() * 1000,\
                            datetime.strptime(df['max'][0], '%Y-%m-%d').timestamp() * 1000
        date = [df['min'][0],df['max'][0]]
        return start_date, end_date,date
    except Exception:

        return "No data", "No data","No data"


def get_entities(r):
    """
    :param r: connection with database
    :return: DataFrame with entities names and their description
            DataFrame with entities which should be showed on fisrst page
    """
    all_entities = """SELECT "Key","description","synonym" FROM name_type order by "order" """
    show_on_first_page = """Select "Key" from name_type where "show" = '+' """

    try:
        df = pd.read_sql(all_entities, r)
        df2 = pd.read_sql(show_on_first_page, r)
        df = df.replace([None], ' ')
        return df, df2
    except Exception:
        df = pd.DataFrame(columns=["Key", "description", "synonym"])
        df2 = pd.DataFrame(columns=['Key'])
        return df, df2


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
        df_min_max=df_min_max.set_index('Key')

        return df, df1,df_min_max
    except Exception:
        df = pd.DataFrame(columns=["Key","description","synonym"] )
        df2 = pd.DataFrame()
        df_min_max = pd.DataFrame()
        return df, df2, df_min_max


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


def get_unit(name,r):
    """ Get number of all patients

     number use only for basic_stats
     """
    try:
        sql = """SELECT "Key","unit" FROM name_type where "Key"='{}' """.format(name)
        df = pd.read_sql(sql, r)
        return df['unit'][0], None
    except Exception:
        return None, "Problem with load data from database"


def get_data(entity, what_table, categorical_filter, categorical, case_id, date, r):
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

    if not categorical_filter and not case_id:
        sql = """SELECT "Name_ID","measurement","Key",array_to_string("Value",';') as "Value" 
                FROM examination_numerical WHERE "Key" IN ({0})  and "Date" Between '{1}' and '{2}'
                UNION
                SELECT "Name_ID","measurement","Key",array_to_string("Value",';') as "Value"
                FROM examination_categorical WHERE "Key" IN ({0}) and "Date" Between '{1}' and '{2}'
                """.format(entity_final,date[0],date[1])

        sql3 = """SELECT * FROM crosstab('SELECT dense_rank() OVER (ORDER BY "Name_ID","measurement")::text AS 
                row_name,"Name_ID","measurement","Date","Key",array_to_string("Value",'';'') as "Value" 
                FROM examination_numerical WHERE  "Key" IN ({0}) 
                            UNION
                SELECT dense_rank() OVER (ORDER BY "Name_ID","measurement")::text AS row_name,"Name_ID","measurement","Date",
                "Key",array_to_string("Value",'';'') as "Value" 
                FROM examination_categorical WHERE "Key" IN ({0})  order by row_name',
                'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by "order"') 
                as ct (row_name text,"Name_ID" text,"measurement" text,"Date" text,{1}) where "Date" Between '{2}' and 
                '{3}' """.format(entity_final, entity_column, date[0], date[1])
    else:
        categorical_filter_str = [x.replace(" is ", "\" in ('").replace(",", "','") for x in categorical_filter]
        categorical_filter_str = '"'+"') and \"".join(categorical_filter_str) + "')"
        categorical_names = "$$" + "$$,$$".join(categorical) + "$$"
        categorical_columns = '"' + '" text,"'.join(categorical) + '" text'
        id_filter_final = "$$"+"$$,$$".join(case_id) + "$$"

        if case_id:
            text = """SELECT "Name_ID" FROM examination WHERE "Billing_ID" in ({0}) """.format(id_filter_final)
        elif categorical_filter:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0})  and "Date" Between '{3}' and '{4}' ')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str,date[0],date[1])
        else:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0})  and "Billing_ID" in ({3})')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str, id_filter_final)

        sql = """SELECT "Name_ID","measurement","Key",array_to_string("Value",';') as "Value" 
                FROM examination_numerical WHERE "Key" IN ({0})  and "Date" Between '{1}' and '{2}'
                and "Name_ID" IN (""".format(entity_final,date[0],date[1]) + text + """) 
                UNION
                SELECT "Name_ID","measurement","Key",array_to_string("Value",';') as "Value" 
                FROM examination_categorical WHERE "Key" IN ({0}) and "Date" Between '{1}' and '{2}' and "Name_ID" 
                IN (""".format(entity_final, date[0], date[1]) + text + """) """

        sql3 = """SELECT * FROM crosstab('SELECT dense_rank() OVER (ORDER BY "Name_ID","measurement")::text AS row_name,
                "Name_ID","measurement","Key",array_to_string("Value",'';'') as "Value" FROM examination_numerical 
                WHERE "Key" IN ({0}) and "Date" Between '{2}' and '{3}' and "Name_ID"
                UNION
                SELECT dense_rank() OVER (ORDER BY "Name_ID","measurement")::text AS row_name,"Name_ID","measurement",
                "Key",array_to_string("Value",'';'') as "Value" 
                FROM examination_categorical WHERE "Key" IN ({0}) and "Date" Between '{2}' and '{3}' and "Name_ID" order by row_name ',
                'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by "order"') 
                as ct (row_name text,"Name_ID" text,"measurement" text,{1}) where "Name_ID" 
                in (""".format(entity_final, entity_column, date[0], date[1]) + text + """) """

    df = pd.read_sql(sql3, r)
    try:
        if what_table == 'long':
            df = pd.read_sql(sql, r)
        else:
            df = pd.read_sql(sql3, r)
            df = df.drop(['row_name'], axis=1)
        return df, None
    except Exception:
        df = pd.DataFrame()
        return df, "Problem with load data from database"


def get_num_values_basic_stats(entity, measurement, categorical_filter, categorical, id_filter,date, r):
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
    if not categorical_filter and not id_filter:
        if round == 'not':
            sql = """SELECT "Key","measurement","instance",count(f."Value"),min(f."Value"),max(f."Value"),AVG(f."Value") 
                    as "mean",stddev(f."Value"),(stddev(f."Value")/sqrt(count(f."Value"))) as "stderr",(percentile_disc(0.5)
                    within group (order by f."Value")) as median FROM examination_numerical,unnest("Value") WITH ordinality 
                    as f ("Value", instance) WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Date" between '{2}' and '{3}' group by "Key","measurement",
                    "instance" order by "Key","measurement","instance" """.format(entity_final, measurement, date[0], date[1])
        else:
            sql = """SELECT "Key","measurement","instance",count(f."Value"),min(f."Value"),max(f."Value"),ROUND(AVG(f."Value")::numeric,2)
                    as "mean",ROUND(stddev(f."Value")::numeric,2),ROUND((stddev(f."Value")/sqrt(count(f."Value")))::numeric,2) as "stderr",(percentile_disc(0.5)
                    within group (order by f."Value")) as median FROM examination_numerical,unnest("Value") WITH ordinality 
                    as f ("Value", instance) WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Date" between '{2}' and '{3}' group by "Key","measurement",
                    "instance" order by "Key","measurement","instance" """.format(entity_final, measurement, date[0], date[1])
    else:
        categorical_filter_str = [x.replace(" is ", "\" in ('").replace(",", "','") for x in categorical_filter]
        categorical_filter_str = '"'+"') and \"".join(categorical_filter_str) + "')"
        categorical_names = "$$" + "$$,$$".join(categorical) + "$$"
        categorical_columns = '"' + '" text,"'.join(categorical) + '" text'
        id_filter_final = "$$"+"$$,$$".join(id_filter) + "$$"

        if id_filter:
            text = """SELECT "Name_ID" FROM examination WHERE "Billing_ID" in ({0}) """.format(id_filter_final)
        elif categorical_filter:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0}) ')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str)
        else:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0})  and "Billing_ID" in ({3})')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str, id_filter_final)

        sql = """SELECT "Key","measurement","instance",count(f."Value"),min(f."Value"),max(f."Value"),AVG(f."Value") as 
                "mean",stddev(f."Value"),(stddev(f."Value")/sqrt(count(f."Value"))) as "stderr",(percentile_disc(0.5) 
                within group (order by f."Value")) as median FROM examination_numerical,unnest("Value") WITH ordinality 
                as f ("Value", instance) WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Date" between '{2}' and '{3}' and "Name_ID" in 
                (""".format(entity_final, measurement,date[0],date[1]) + text + """)  group by "Key","measurement","instance" 
                order by "Key","measurement","instance" """

    try:
        df = pd.read_sql(sql, r)
        df = df.round(2)
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_cat_values_basic_stats(entity,measurement, categorical_filter, categorical, id_filter, r):
    """ Get number of categorical values from database

    get_cat_values_basic_stas use only for basic_stas categorical

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Key,count

    """

    entity_final = "$$" + "$$,$$".join(entity) + "$$"
    measurement = "'" + "','".join(measurement) + "'"

    if not categorical_filter and not id_filter:
        sql = """SELECT "Key","measurement",number,count("Key") FROM examination_categorical,array_length("Value",1) 
                as f (number) WHERE "Key" IN ({0}) and "measurement" IN ({1}) group by "measurement","Key",number """\
            .format(entity_final, measurement)
    else:
        categorical_filter_str = [x.replace(" is ", "\" in ('").replace(",", "','") for x in categorical_filter]
        categorical_filter_str = '"'+"') and \"".join(categorical_filter_str) + "')"
        categorical_names = "$$" + "$$,$$".join(categorical) + "$$"
        categorical_columns = '"' + '" text,"'.join(categorical) + '" text'
        id_filter_final = "$$"+"$$,$$".join(id_filter) + "$$"

        if id_filter:
            text = """SELECT "Name_ID" FROM examination WHERE "Billing_ID" in ({0}) """.format(id_filter_final)
        elif categorical_filter:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0}) ')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str)
        else:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0})  and "Billing_ID" in ({3})')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str, id_filter_final)

        sql = """SELECT "Key","measurement",number,count("Key") FROM examination_categorical,array_length("Value",1) 
            as f (number) WHERE "Key" IN ({0}) and "measurement" IN ({1}) and "Name_ID" 
            in (""".format(entity_final, measurement) + text + """)  group by "measurement","Key",number """

    try:
        df = pd.read_sql(sql, r)
        return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_values_scatter_plot(x_entity, y_entity, x_measurement,y_measurement, categorical_filter, categorical, id_filter,date, r):
    """ Get numerical values from numerical table  from database

    get_values use in scatter plot, coplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity1,entity2,...

    """
    if not categorical_filter and not id_filter:
        sql = """SELECT "Name_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "measurement"= '{1}' and "Date" between '{2}' and '{3}' Group by "Name_ID","measurement","Key" 
                order by "measurement"  """.format(x_entity, x_measurement, date[0], date[1])
        sql2 = """SELECT "Name_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "measurement"= '{1}'  and "Date" between '{2}' and '{3}'Group by "Name_ID","measurement","Key" 
                order by "measurement" """.format(y_entity, y_measurement, date[0], date[1])

    else:
        categorical_filter_str = [x.replace(" is ", "\" in ('").replace(",", "','") for x in categorical_filter]
        categorical_filter_str = '"'+"') and \"".join(categorical_filter_str) + "')"
        categorical_names = "$$" + "$$,$$".join(categorical) + "$$"
        categorical_columns = '"' + '" text,"'.join(categorical) + '" text'
        id_filter_final = "$$"+"$$,$$".join(id_filter) + "$$"

        if id_filter:
            text = """SELECT "Name_ID" FROM examination WHERE "Billing_ID" in ({0}) """.format(id_filter_final)
        elif categorical_filter:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0}) ')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str)
        else:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0})  and "Billing_ID" in ({3})')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str, id_filter_final)

        sql = """SELECT "Name_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "measurement"= '{1}' and "Date" between '{2}' and '{3}' and "Name_ID" in (""".format(x_entity, x_measurement,date[0],date[1]) \
              + text + """) Group by "Name_ID","measurement","Key" order by "measurement"  """
        sql2 = """SELECT "Name_ID",AVG(f."Value") as "{0}" FROM examination_numerical,unnest("Value") as f ("Value")  
                WHERE "Key" IN ('{0}') and "measurement"= '{1}' and "Date" between '{2}' and '{3}' and "Name_ID" in (""".format(y_entity, y_measurement,date[0],date[1]) \
               + text + """) Group by "Name_ID","measurement","Key" order by "measurement" """

        # load data with Gene symbol remove in case of Patient data
        sql3 = """SELECT en."Name_ID",min(fc."Value") as "GeneSymbol",AVG(f."Value") as "{0}" FROM examination_numerical 
                as en left join examination_categorical as ec on en."Name_ID" = ec."Name_ID",unnest(en."Value") 
                as f ("Value"),unnest(ec."Value") as fc ("Value") WHERE en."Key" IN ('{0}') and en."measurement"= '{1}' 
                and ec."Key" ='GeneSymbol' and en."Name_ID" in (""".format(x_entity, x_measurement) + text + """)
                 Group by en."Name_ID",ec."Key",en."measurement",en."Key" order by en."measurement"  """
        sql4 = """SELECT en."Name_ID",min(fc."Value") as "GeneSymbol",AVG(f."Value") as "{0}" FROM examination_numerical
                as en left join examination_categorical as ec on en."Name_ID" = ec."Name_ID",unnest(en."Value") 
                as f ("Value"),unnest(ec."Value") as fc ("Value") WHERE en."Key" IN ('{0}') and en."measurement"= '{1}' 
                and ec."Key" ='GeneSymbol' and en."Name_ID" in (""".format(y_entity, y_measurement) + text + """)
                 Group by en."Name_ID",ec."Key",en."measurement",en."Key" order by en."measurement"  """

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


def get_cat_values(entity, subcategory, measurement, categorical_filter, categorical, id_filter, r):
    """ Get categorical values from database

    get_cat_values use in scatter plot and coplots

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity

    """

    subcategory_final = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not id_filter:
        sql = """SELECT "Name_ID",string_agg(distinct f."Value",',') FROM examination_categorical,unnest("Value") 
        as f ("Value") WHERE "Key"= '{0}' and f."Value" IN ({1})  and "measurement" IN ({2}) Group by "Name_ID" 
        order by string_agg(distinct f."Value",',')""".format(entity, subcategory_final, measurement)

    else:
        categorical_filter_str = [x.replace(" is ", "\" in ('").replace(",", "','") for x in categorical_filter]
        categorical_filter_str = '"'+"') and \"".join(categorical_filter_str) + "')"
        categorical_names = "$$" + "$$,$$".join(categorical) + "$$"
        categorical_columns = '"' + '" text,"'.join(categorical) + '" text'
        id_filter_final = "$$"+"$$,$$".join(id_filter) + "$$"

        if id_filter:
            text = """SELECT "Name_ID" FROM examination WHERE "Billing_ID" in ({0}) """.format(id_filter_final)
        elif categorical_filter:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0}) ')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str)
        else:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0})  and "Billing_ID" in ({3})')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str, id_filter_final)

        sql = """SELECT "Name_ID",string_agg(distinct f."Value",',') FROM examination_categorical,unnest("Value") 
                as f ("Value") WHERE "Key"= '{0}' and f."Value" IN ({1})  and "measurement" IN ({2} )and "Name_ID" 
                in (""".format(entity, subcategory_final,measurement) + text + """)
                Group by "Name_ID" order by string_agg(distinct f."Value",',')"""

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return None, "The entity {} wasn't measured".format(entity)
    else:
        df.columns = ["Name_ID", entity]
        return df, None


def get_cat_values_barchart(entity, subcategory,measurement,categorical_filter,categorical,id_filter,date, r):
    """ Get number of subcategory values from database

    get_cat_values_barchart use only for barchart

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,Key,Value

    """

    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not id_filter:
        sql = """SELECT "Value","measurement",count("Value") FROM examination_categorical WHERE "Key"='{0}' and "Date" BETWEEN '{3}' and '{4}'
                and "measurement" IN ({2}) and ARRAY{1} && "Value"  group by "Value","measurement" """.format(entity, subcategory, measurement,date[0],date[1])
    else:
        categorical_filter_str = [x.replace(" is ", "\" in ('").replace(",", "','") for x in categorical_filter]
        categorical_filter_str = '"'+"') and \"".join(categorical_filter_str) + "')"
        categorical_names = "$$" + "$$,$$".join(categorical) + "$$"
        categorical_columns = '"' + '" text,"'.join(categorical) + '" text'
        id_filter_final = "$$"+"$$,$$".join(id_filter) + "$$"

        if id_filter:
            text = """SELECT "Name_ID" FROM examination WHERE "Billing_ID" in ({0}) """.format(id_filter_final)
        elif categorical_filter:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0}) ')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str)
        else:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0})  and "Billing_ID" in ({3})')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str, id_filter_final)

        sql = """SELECT "Value","measurement",count("Value") FROM examination_categorical WHERE "Key"='{0}' and "measurement" IN ({2})
                and ARRAY{1} && "Value" and "Name_ID" in (""".format(entity, subcategory, measurement) + text + """)  group by "Value","measurement" """

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


def get_num_cat_values(entity_num, entity_cat, subcategory,measurement, categorical_filter, categorical, id_filter, date, r):
    """ Retrieve categorical and numerical value

    get_num_cat_values use in histogram and boxplot

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity_num,entity_cat
     """
    subcategory = "$$" + "$$,$$".join(subcategory) + "$$"
    measurement = "'" + "','".join(measurement) + "'"
    if not categorical_filter and not id_filter:
        sql = """SELECT en."Name_ID",en."measurement",AVG(a."Value") as "{0}",STRING_AGG(distinct f."Value", ',') 
        as "{1}" FROM examination_numerical as en left join examination_categorical as ec 
        on en."Name_ID" = ec."Name_ID",unnest(en."Value") as a ("Value"),unnest(ec."Value") as f ("Value") 
        where en."Key" = '{0}' and ec."Key" = '{1}' and en."measurement" IN ({3}) and ec."measurement" IN ({3}) 
        and en."Date" Between '{4}' and '{5}' 
        and f."Value" IN ({2}) group by en."Name_ID",en."measurement",ec."measurement" order by en."Name_ID",en."measurement" """.format(
            entity_num, entity_cat, subcategory, measurement,date[0],date[1])
    else:
        categorical_filter_str = [x.replace(" is ", "\" in ('").replace(",", "','") for x in categorical_filter]
        categorical_filter_str = '"'+"') and \"".join(categorical_filter_str) + "')"
        categorical_names = "$$" + "$$,$$".join(categorical) + "$$"
        categorical_columns = '"' + '" text,"'.join(categorical) + '" text'
        id_filter_final = "$$"+"$$,$$".join(id_filter) + "$$"

        if id_filter:
            text = """SELECT "Name_ID" FROM examination WHERE "Billing_ID" in ({0}) """.format(id_filter_final)
        elif categorical_filter:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0}) ')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str)
        else:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0})  and "Billing_ID" in ({3})')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str, id_filter_final)

        sql = """SELECT en."Name_ID",en."measurement",AVG(a."Value") as "{0}",STRING_AGG(distinct f."Value", ',') as "{1}" FROM examination_numerical as en
                        left join examination_categorical as ec on en."Name_ID" = ec."Name_ID",unnest(en."Value") as a ("Value"),unnest(ec."Value") as f ("Value") 
                        where en."Key" = '{0}' and ec."Key" = '{1}' and en."measurement" IN ({3}) and ec."measurement" IN ({3}) 
                        and f."Value" IN ({2}) and en."Name_ID" in (""".format(
            entity_num, entity_cat, subcategory, measurement)+ text +""") group by en."Name_ID",en."measurement",ec."measurement" order by en."Name_ID",en."measurement" """

    try:
        df = pd.read_sql(sql, r)
    except Exception:
        return None, "Problem with load data from database"
    if df.empty or len(df) == 0:
        return df, "The entity {0} or {1} wasn't measured".format(entity_num,entity_cat)
    else:
        return df, None


def get_values_heatmap(entity,measurement,categorical_filter, categorical, id_filter,date, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"

    if not categorical_filter and not id_filter:
        sql = """SELECT "Name_ID","measurement","Key",AVG(f."Value") as "Value" FROM examination_numerical, 
            unnest("Value") as f("Value") WHERE "Key" IN ({0}) and "measurement" in ('{1}') and "Date" Between '{2}' and '{3}'
                Group by "Name_ID","measurement","Key" """.format(entity_fin, measurement, date[0], date[1])
    else:
        categorical_filter_str = [x.replace(" is ", "\" in ('").replace(",", "','") for x in categorical_filter]
        categorical_filter_str = '"'+"') and \"".join(categorical_filter_str) + "')"
        categorical_names = "$$" + "$$,$$".join(categorical) + "$$"
        categorical_columns = '"' + '" text,"'.join(categorical) + '" text'
        id_filter_final = "$$"+"$$,$$".join(id_filter) + "$$"

        if id_filter:
            text = """SELECT "Name_ID" FROM examination WHERE "Billing_ID" in ({0}) """.format(id_filter_final)
        elif categorical_filter:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0}) ')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str)
        else:
            text = """SELECT "Name_ID" FROM crosstab('SELECT "Name_ID","Key",array_to_string("Value",'';'') as "Value" 
                    FROM examination_categorical WHERE "Key" IN ({0})  and "Billing_ID" in ({3})')
                    AS CT ("Name_ID" text,{1}) where {2} """.format(categorical_names, categorical_columns,
                                                                    categorical_filter_str, id_filter_final)

        sql = """SELECT "Name_ID","measurement","Key",AVG(f."Value") as "Value" FROM examination_numerical, 
                unnest("Value") as f("Value") WHERE "Key" IN ({0}) and "measurement" in ('{1}') and "Date" Between '{2}' and '{3}'
                 and "Name_ID" in (""".format(entity_fin,measurement, date[0], date[1])+text+""")
                Group by "Name_ID","measurement","Key" """


    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Name_ID"], columns="Key", values="Value", aggfunc=np.mean).reset_index()
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_values_cat_heatmap(entity,measurement, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"

    sql = """SELECT "Name_ID","Key","Value"[1] as "Value" FROM examination_categorical WHERE "Key" IN ({0}) """.format(entity_fin,measurement)

    try:
        df = pd.read_sql(sql, r)
        df = df.pivot_table(index=["Name_ID"], columns="Key", values="Value", aggfunc=min).reset_index()
        if df.empty or len(df) == 0:
            return df, "The entity wasn't measured"
        else:
            return df, None
    except Exception:
        return None, "Problem with load data from database"


def get_values_clustering(entity, r):
    """ Get numerical values from numerical table  from database

    get_values use in heatmap, clustering

    r: connection with database

    Returns
    -------
    df: DataFrame with columns Name_ID,entity1,entity2,...

    """

    entity_fin = "$$" + "$$,$$".join(entity) + "$$"
    entity_fin2 = '"'+'" text,"'.join(entity) + '" text'

    sql2 = """SELECT * FROM crosstab('SELECT en."Name_ID",en."Key",array_to_string(en."Value",'';'') 
                as "Value" FROM examination_numerical as en WHERE en."Key" IN ({0}) 
        UNION
            SELECT ec."Name_ID",ec."Key",array_to_string(ec."Value",'';'') as "Value" FROM examination_categorical as ec WHERE ec."Key" IN ({0})',
            'SELECT "Key" FROM name_type WHERE "Key" IN ({0}) order by "order"') 
            as ct ("Name_ID" text,{1})""".format(entity_fin,entity_fin2)

    try:
        df = pd.read_sql(sql2, r)

        return df, None

    except Exception:
        return None, "Problem with load data from database"

